from apkmirror import Version
from utils import patch_apk


def build_apks(latest_version: Version):
    # patch
    apk = "big_file_merged.apk"
    patches = "bins/patches.mpp"
    cli = "bins/morphe-cli.jar"

    common_includes = [
        "Hide ads",
        "Video ads",
        "Disable double tap actions",
        "Double tap to seek",
        "Downloads",
        "Disable haptic feedback",
        "Loop video",
        "Play all",
        "Reload video",
        "Save to watch later",
        "Seekbar",
        "Swipe controls",
        "Hide video action buttons",
        "Navigation bar",
        "Hide player overlay buttons",
        "Captions",
        "Hide autoplay preview",
        "Hide end screen cards",
        "Hide end screen suggested video",
        "Hide layout components",
        "Hide info cards",
        "Hide player flyout menu components",
        "Disable player popup panels",
        "Hide related videos",
        "Disable rolling number animations",
        "Hide Shorts components",
        "Disable sign in to TV popup",
        "Miniplayer",
        "Override YouTube Music buttons",
        "Shorts autoplay",
        "Disable Shorts resuming on startup",
        "SponsorBlock",
        "Change start page",
        "Theme",
        "Remove background playback restrictions",
        "Bypass URL redirects",
        "Open links externally",
        "Sanitize sharing links",
        "Open system share sheet",
        "Force original audio",
        "Video quality",
        "Playback speed",
        "Copy video URL",
        "Change form factor",
    ]

    common_excludes = []

    patch_apk(
        cli,
        patches,
        apk,
        includes=common_includes,
        excludes=common_excludes,
        out=f"yt-morphe-v{latest_version.version}.apk",
    )

    patch_apk(
        cli,
        patches,
        apk,
        includes=["GmsCore support"] + ["Spoof video streams"] + common_includes,
        excludes=common_excludes,
        out=f"yt-microg-morphe-v{latest_version.version}.apk",
    )
