from apkmirror import Version
from utils import patch_apk


def build_apks(latest_version: Version):
    # patch
    apk = "big_file_merged.apk"
    patches = "bins/patches.rvp"
    cli = "bins/cli.jar"

    common_includes = [
        "Change live ring click action",
        "Change share sheet",
        "Change start page",
        "Custom branding icon for YouTube",
        "Custom Shorts action buttons",
        "Description components",
        "Disable auto captions",
        "Disable haptic feedback",
        "Disable resuming Shorts on startup",
        "Disable splash animation",
        "Enable external browser",
        "Enable open links directly",
        "Force hide player buttons background",
        "Fullscreen components",
        "Hide Shorts dimming",
        "Hide action buttons",
        "Hide ads",
        "Hide comments components",
        "Hide feed components",
        "Hide feed flyout menu",
        "Hide layout components",
        "Hide player buttons",
        "Hide player flyout menu",
        "Hook download actions",
        "Navigation bar components",
        "Overlay buttons",
        "Player components",
        "Remove background playback restrictions",
        "Sanitize sharing links",
        "Seekbar components",
        "Settings for YouTube",
        "Shorts components",
        "SponsorBlock",
        "Theme",
        "Toolbar components",
        "Video playback",
        "Visual preferences icons for YouTube",
    ]

    patch_apk(
        cli,
        patches,
        apk,
        includes=common_includes,
        out=f"yt-rvx-v{latest_version.version}.apk",
    )

    patch_apk(
        cli,
        patches,
        apk,
        includes=["GmsCore support"] + common_includes,
        out=f"microg-rvx-v{latest_version.version}.apk",
    )
