from apkmirror import Version
from utils import patch_apk


def build_apks(latest_version: Version):
    # patch
    apk = "big_file_merged.apk"
    patches = "bins/patches.mpp"
    cli = "bins/morphe-cli.jar"

    common_includes = [
        "Hook feature flag",
        "Custom download folder",
        "Clear tracking params",
        "Customize Navigation Bar items",
        "Custom sharing domain",
        "Delete from database",
        "Disable auto timeline scroll on launch",
        "Download patch",
        "Native downloader",
        "Native reader mode",
        "Enable PiP mode automatically",
        "Disable chirp font",
        "Enable Undo Posts",
        "Customize explore tabs",
        "Import/Export login token",
        "Native translator",
        "Force enable translate",
        "Customize Inline action Bar items",
        "Legacy share links",
        "Customize profile tabs",
        "Remove premium upsell",
        "Hide promote button",
        "Hide FAB",
        "Customize search tab items",
        "Selectable Text",
        "Show poll results",
        "Customize side bar items",
        "Customize timeline top bar",
        "Remove Ads",
        "Hide recommendation items",
        "Handle custom twitter links",
        "Show sensitive media",
        "Add ability to copy media link",
        "Bring back twitter",
        "Hide Banner",
    ]

    common_excludes = []

    patch_apk(
        cli,
        patches,
        apk,
        includes=["Bring back twitter"] + common_includes,
        excludes=["Dynamic color"] + common_excludes,
        out=f"twitter-piko-v{latest_version.version}.apk",
    )
