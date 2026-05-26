from apkmirror import Version
from utils import patch_apk


def build_apks(latest_version: Version):
    # patch
    apk = "big_file_merged.apk"
    patches = "bins/patches.mpp"
    cli = "bins/morphe-cli.jar"

    common_includes = [
        "Copy video URL",
    ]

    common_excludes = []

    patch_apk(
        cli,
        patches,
        apk,
        includes=common_includes,
        excludes=["Dynamic color"] + common_excludes,
        out=f"yt-morphe-v{latest_version.version}.apk",
    )
