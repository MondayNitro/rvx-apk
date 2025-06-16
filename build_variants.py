from apkmirror import Version
from utils import patch_apk


def build_apks(latest_version: Version):
    # patch
    apk = "big_file_merged.apk"
    patches = "bins/patches.rvp"
    cli = "bins/cli.jar"

    common_includes = [
        "Bypass URL redirects",
        "Bypass image region restrictions",
        "Change form factor",
        "Change start page",
        "Copy video URL",
        "Disable HDR video",
        "Disable auto captions",
        "Disable haptic feedback",
        "Disable player popup panels",
        "Disable resuming Shorts on startup",
        "Downloads",
        "Force original audio",
        "Hide Shorts components",
        "Hide ads",
        "Hide end screen cards",
        "Hide end screen suggested video",
        "Hide info cards",
        "Hide layout components",
        "Hide player flyout menu items",
        "Hide player overlay buttons",
        "Hide video action buttons",
        "Navigation buttons",
        "Open Shorts in regular player",
        "Open links externally",
        "Playback speed",
        "Remove background playback restrictions",
        "Remove tracking query parameter",
        "Seekbar",
        "SponsorBlock",
        "Swipe controls",
        "Theme",
        "Video ads",
        "Video quality",
    ]

    patch_apk(
        cli,
        patches,
        apk,
        includes=common_includes,
        out=f"yt-revanced-v{latest_version.version}.apk",
    )

    patch_apk(
        cli,
        patches,
        apk,
        includes=["GmsCore support", "Spoof video streams"] + common_includes,
        out=f"microg-revanced-v{latest_version.version}.apk",
    )
    