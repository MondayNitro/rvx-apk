from apkmirror import Version, Variant
from build_variants import build_apks
from download_bins import download_apkeditor, download_revanced_bins
import github
from utils import panic, merge_apk, publish_release
from download_bins import download_release_asset
import apkmirror
import os
import shutil
import zipfile


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

    with zipfile.ZipFile("big_file.apkm", "r") as zip_ref:
        zip_ref.extractall("extracted_bundle")

    files_to_keep = ["base.apk", "split_config.armeabi_v7a.apk", "split_config.en.apk", "split_config.hdpi.apk", "split_config.xhdpi.apk", "split_config.xxhdpi.apk"]

    def keep_files_recursively(directory, files_to_keep):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file not in files_to_keep:
                    os.remove(os.path.join(root, file))
            for dir in dirs:
                if dir not in files_to_keep:
                    shutil.rmtree(os.path.join(root, dir))

    keep_files_recursively("extracted_bundle", files_to_keep)

    # Create a new ZIP archive with the remaining files
    with zipfile.ZipFile(f"youtube-bundle-v{desired_version}.apks", "w") as zip_ref:
        for root, dirs, files in os.walk("extracted_bundle"):
            for file in files:
                zip_ref.write(os.path.join(root, file), os.path.join(os.path.relpath(root, "extracted_bundle"), file))

    # Delete the extracted_bundle directory
    shutil.rmtree("extracted_bundle")
    
    download_apkeditor()

    if not os.path.exists("big_file_merged.apk"):
        merge_apk(f"youtube-bundle-v{desired_version}.apks")
    else:
        print("apk bundle is already merged")

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

    publish_release(
        f"{latest_version.version}_{rvxRelease['tag_name']}",
        [
            f"yt-rvx-v{latest_version.version}.apk",
            f"microg-rvx-v{latest_version.version}.apk",
            f"youtube-bundle-v{desired_version}.apks",
        ],
        message,
    )


if __name__ == "__main__":
    main()
