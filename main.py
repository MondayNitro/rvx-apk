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


def process(latest_version: Version):
    variants: list[Variant] = apkmirror.get_variants(latest_version)

    download_link: Variant | None = None
    for variant in variants:
        if variant.is_bundle and variant.architecture == "universal":
            download_link = variant
            break

    if download_link is None:
        bundle_variants = [v for v in variants if v.is_bundle]
        if not bundle_variants:
            raise Exception("Bundle not Found")

        fallback = next((v for v in bundle_variants if v.architecture == "arm64-v8a"), None)
        download_link = fallback or bundle_variants[0]
        print(f"Universal bundle not found, falling back to {download_link.architecture}")

    apkmirror.download_apk(download_link)
    if not os.path.exists("big_file.apkm"):
        panic("Failed to download apk")

    with zipfile.ZipFile("big_file.apkm", "r") as zip_ref:
        zip_ref.extractall("big_file")

    files_to_keep = {
        "base.apk",
        "split_config.arm64_v8a.apk",
        "split_config.en.apk",
        "split_config.xhdpi.apk",
        "split_config.xxhdpi.apk",
    }

    keep_files_recursively("big_file", files_to_keep)

    download_apkeditor()

    if not os.path.exists("big_file_merged.apk"):
        merge_apk("big_file")
    else:
        print("apkm is already merged")

    shutil.make_archive("big_file", "zip", "big_file")
    os.rename("big_file.zip", "big_file.apks")
    shutil.rmtree("big_file")

    download_morphe_cli(include_prereleases=True)

    print("Downloading patches")
    morpheRelease = download_release_asset(
        "MorpheApp/morphe-patches", "^patches.*mpp$", "bins", "patches.mpp", include_prereleases=True
    )

    message: str = f"""
Changelogs:
[morphe-{morpheRelease["tag_name"]}]({morpheRelease["html_url"]})
"""

    build_apks(latest_version)

    os.rename("big_file.apks", f"youtube-bundle-v{latest_version.version}.apks")

    publish_release(
        f"{latest_version.version}_{morpheRelease['tag_name']}",
        [
            f"yt-morphe-v{latest_version.version}.apk",
            f"yt-microg-morphe-v{latest_version.version}.apk",
            f"youtube-bundle-v{latest_version.version}.apks",
        ],
        message,
        f"{latest_version.version}_{morpheRelease['tag_name']}"
    )


def main():
    # get latest version
    url: str = "https://www.apkmirror.com/apk/google-inc/youtube/"
    repo_url: str = REPO

    versions = apkmirror.get_versions(url)

    latest_version = get_latest_release(versions)
    if latest_version is None:
        raise Exception("Could not find the latest version")

    # only continue if it's a release
    if latest_version.version.find("release") < 0:
        panic("Latest version is not a release version")

    last_build_version: github.GithubRelease | None = github.get_last_build_version(
        repo_url
    )

    if last_build_version is None:
        panic("Failed to fetch the latest build version")
        return

    # Begin stuff
    morphe_patches_version = get_latest_morphe_patches_version()

    expected_tag = f"{latest_version.version}_{morphe_patches_version}"
    if last_build_version.tag_name != expected_tag:
        print(f"New version found: {expected_tag}")
    else:
        print("No new version found")
        return

    process(latest_version)


def manual(version: str):
    link = f'https://www.apkmirror.com/apk/google-inc/youtube/youtube-{version.replace(".","-")}-release'
    latest_version = Version(link=link, version=version)

    repo_url: str = REPO

    last_build_version: github.GithubRelease | None = github.get_last_build_version(
        repo_url
    )

    if last_build_version is None:
        panic("Failed to fetch the latest build version")
        return

    morphe_patches_version = get_latest_piko_patches_version()

    expected_tag = f"{latest_version.version}_{morphe_patches_version}"

    if last_build_version.tag_name == expected_tag:
        print("No new version found")
        return

    process(latest_version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Morphe APK')
    # 0 = auto; 1 = manual;
    parser.add_argument('--m', action="store", dest='mode', default=0)
    parser.add_argument('--v', action="store", dest='version', default=0)

    args = parser.parse_args()
    mode = args.mode

    if not mode: # auto
        main()
    else: # manual
        version = args.version
        if not version:
            raise Exception("Version is required.")
        manual(version)
