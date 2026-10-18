from dataclasses import dataclass
from apkmirror import Version, Variant
from build_variants import build_apks
from download_bins import download_apkeditor, download_morphe_cli, download_release_asset
import github
from utils import panic, merge_apk, publish_release
from constants import REPO
import apkmirror
import os
import argparse
import shutil
import requests
import zipfile


@dataclass(frozen=True)
class App:
    key: str
    name: str
    apkmirror_url: str
    slug: str
    package: str
    prefix: str


FILES_TO_KEEP = {
    "base.apk",
    "split_config.arm64_v8a.apk",
    "split_config.en.apk",
    "split_config.xhdpi.apk",
    "split_config.xxhdpi.apk",
}


APPS: dict[str, App] = {
    "youtube": App(
        key="youtube",
        name="YouTube",
        apkmirror_url="https://www.apkmirror.com/apk/google-inc/youtube/",
        slug="youtube",
        package="com.google.android.youtube",
        prefix="youtube",
    ),
    "music": App(
        key="music",
        name="YouTube Music",
        apkmirror_url="https://www.apkmirror.com/apk/google-inc/youtube-music/",
        slug="youtube-music",
        package="com.google.android.apps.youtube.music",
        prefix="youtube-music",
    ),
}


def get_latest_release(versions: list[Version]) -> Version | None:
    for i in versions:
        if i.version.find("release") >= 0:
            return i


def get_latest_morphe_patches_version(
    url="https://api.github.com/repos/MorpheApp/morphe-patches/releases"
):
    response = requests.get(url)
    releases_data = response.json()

    for release in releases_data:
        tag_name = release.get("tag_name")
        if tag_name:
            return tag_name


def keep_files_recursively(directory: str, files_to_keep: set[str]):
    for root, _, files in os.walk(directory):
        for file in files:
            if file not in files_to_keep:
                os.remove(os.path.join(root, file))


def cleanup_workdir():
    """Remove leftovers so building several apps in one run doesn't mix files."""
    for f in ("big_file.apkm", "big_file_merged.apk", "big_file.apks", "big_file.zip"):
        if os.path.exists(f):
            os.remove(f)
    if os.path.isdir("big_file"):
        shutil.rmtree("big_file")


def build_app(app: App, latest_version: Version) -> list[str]:
    """Download, merge and patch one app. Returns the files to publish."""
    print(f"[{app.key}] Building {latest_version.version}")
    cleanup_workdir()

    variants: list[Variant] = apkmirror.get_variants(latest_version)

    download_link: Variant | None = None
    for variant in variants:
        if variant.is_bundle and variant.architecture == "universal":
            download_link = variant
            break

    if download_link is None:
        bundle_variants = [v for v in variants if v.is_bundle]
        if not bundle_variants:
            raise Exception(f"[{app.key}] Bundle not Found")

        fallback = next((v for v in bundle_variants if v.architecture == "arm64-v8a"), None)
        download_link = fallback or bundle_variants[0]
        print(f"Universal bundle not found, falling back to {download_link.architecture}")

    apkmirror.download_apk(download_link)
    if not os.path.exists("big_file.apkm"):
        panic("Failed to download apk")

    with zipfile.ZipFile("big_file.apkm", "r") as zip_ref:
        zip_ref.extractall("big_file")

    keep_files_recursively("big_file", FILES_TO_KEEP)

    if not os.path.exists("big_file_merged.apk"):
        merge_apk("big_file")
    else:
        print("apkm is already merged")

    shutil.make_archive("big_file", "zip", "big_file")
    os.rename("big_file.zip", "big_file.apks")
    shutil.rmtree("big_file")

    build_apks(latest_version, app)

    bundle_name = f"{app.prefix}-bundle-v{latest_version.version}.apks"
    os.rename("big_file.apks", bundle_name)

    return [
        f"{app.prefix}-morphe-v{latest_version.version}.apk",
        f"{app.prefix}-microg-morphe-v{latest_version.version}.apk",
        bundle_name,
    ]


def release(builds: list[tuple[App, Version]]):
    """Build every app in `builds` and publish ONE release tagged with the patches version."""
    morphe_patches_version = get_latest_morphe_patches_version()
    if not morphe_patches_version:
        panic("Failed to fetch the latest morphe patches version")
        return

    if github.get_release_by_tag(REPO, morphe_patches_version) is not None:
        print(f"Release {morphe_patches_version} already exists, nothing to do")
        return

    print(f"New patches version found: {morphe_patches_version}")

    download_apkeditor()
    download_morphe_cli(include_prereleases=True)

    print("Downloading patches")
    morpheRelease = download_release_asset(
        "MorpheApp/morphe-patches", "^patches.*mpp$", "bins", "patches.mpp", include_prereleases=True
    )

    files: list[str] = []
    for app, version in builds:
        files += build_app(app, version)

    built_from = "\n".join(f"- {app.name} {version.version}" for app, version in builds)
    message: str = f"""
Changelogs:
[morphe-{morpheRelease["tag_name"]}]({morpheRelease["html_url"]})

Built from:
{built_from}
"""

    tag = morpheRelease["tag_name"]
    publish_release(tag, files, message, tag)


def main():
    builds: list[tuple[App, Version]] = []
    for app in APPS.values():
        versions = apkmirror.get_versions(app.apkmirror_url)

        latest_version = get_latest_release(versions)
        if latest_version is None:
            raise Exception(f"[{app.key}] Could not find the latest version")

        builds.append((app, latest_version))

    release(builds)


def manual(youtube_version: str, music_version: str):
    builds: list[tuple[App, Version]] = []

    for app, version in (
        (APPS["youtube"], youtube_version),
        (APPS["music"], music_version),
    ):
        if not version:
            continue
        link = f'https://www.apkmirror.com/apk/google-inc/{app.slug}/{app.slug}-{version.replace(".", "-")}-release'
        builds.append((app, Version(link=link, version=version)))

    if not builds:
        raise Exception("Provide at least one of --youtube / --music.")

    release(builds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Morphe APK')
    # 0 = auto; 1 = manual;
    parser.add_argument('--m', action="store", dest='mode', default=0)
    parser.add_argument('--youtube', action="store", dest='youtube', default="")
    parser.add_argument('--music', action="store", dest='music', default="")

    args = parser.parse_args()

    if not args.mode:  # auto
        main()
    else:  # manual
        manual(args.youtube, args.music)
