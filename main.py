from apkmirror import Version, Variant
from build_variants import build_apks
from download_bins import download_apkeditor, download_revanced_bins
import github
from utils import panic, merge_apk, publish_release
from download_bins import download_release_asset
import apkmirror
import os


def main():
    # Specify the desired version
    desired_version = "19.16.39"

    # Format the version for the URL
    formatted_version = desired_version.replace(".", "-")

    # Download the specific version
    url = f"https://www.apkmirror.com/apk/google-inc/youtube/youtube-{formatted_version}-release/"
    
    repo_url: str = "MondayNitro/rvx-apk"

    latest_version = Version(link=url,version=desired_version)

    last_build_version: github.GithubRelease | None = github.get_last_build_version(
        repo_url
    )

    if last_build_version is None:
        panic("Failed to fetch the latest build version")
        return

    # Begin stuff
    if last_build_version.tag_name != latest_version.version:
        print(f"New version found: {latest_version.version}")
    else:
        print("No new version found")
        return

    # get bundle and universal variant
    variants: list[Variant] = apkmirror.get_variants(latest_version)

    download_link: Variant | None = None
    for variant in variants:
        if variant.is_bundle and variant.arcithecture == "universal":
            download_link = variant
            break

    if download_link is None:
        raise Exception("Bundle not Found")

    apkmirror.download_apk(download_link)
    if not os.path.exists("big_file.apkm"):
        panic("Failed to download apk")

    download_apkeditor()

    if not os.path.exists("big_file_merged.apk"):
        merge_apk("big_file.apkm")
    else:
        print("apkm is already merged")

    download_revanced_bins()

    print("Downloading patches")
    rvxRelease = download_release_asset(
        "inotia00/revanced-patches", "^rev.*jar$", "bins", "patches.jar"
    )

    print("Downloading integrations")
    integrationsRelease = download_release_asset(
        "inotia00/revanced-integrations",
        "^rev.*apk$",
        "bins",
        "integrations.apk",
    )

    print(integrationsRelease["body"])

    message: str = f"""
Changelogs:
[rvx-{rvxRelease["tag_name"]}]({rvxRelease["html_url"]})
[integrations-{integrationsRelease["tag_name"]}]({integrationsRelease["html_url"]})
"""

    build_apks(latest_version)

    # Rename big_file.apkm using the desired_version
os.rename("big_file.apkm", f"youtube-bundle-v{desired_version}.apkm")

    publish_release(
        f"{latest_version.version}_{rvxRelease['tag_name']}",
        [
            f"yt-rvx-v{latest_version.version}.apk",
            f"microg-rvx-v{latest_version.version}.apk",
            f"youtube-bundle-v{desired_version}.apkm",
        ],
        message,
    )

    # Add the renamed file to the assets list
    assets.append(new_filename)


if __name__ == "__main__":
    main()
