from apkmirror import Version
from utils import patch_apk

YOUTUBE_INCLUDES = [
    "Add to queue",
    "Bypass link redirects",
    "Bypass URL redirects",
    "Captions",
    "Change form factor",
    "Change start page",
    "Channel search",
    "Copy video link",
    "Disable continue watching prompt",
    "Disable fullscreen gestures",
    "Disable haptic feedback",
    "Disable player popup panels",
    "Disable playlist autoplay",
    "Disable rolling number animations",
    "Disable Shorts resuming on startup",
    "Disable sign in to TV popup",
    "Double tap to seek",
    "Downloads",
    "Force original audio",
    "Fullscreen video scale",
    "Hide ads",
    "Hide autoplay preview",
    "Hide end screen cards",
    "Hide end screen suggested video",
    "Hide info cards",
    "Hide layout components",
    "Hide player flyout menu components",
    "Hide player overlay buttons",
    "Hide related videos",
    "Hide Shorts components",
    "Hide video action buttons",
    "Loop video",
    "Miniplayer",
    "Mute button",
    "Navigation bar",
    "Open links externally",
    "Open system share sheet",
    "Override YouTube Music buttons",
    "Picture-in-picture button",
    "Play all",
    "Playback speed",
    "Reload video",
    "Remove background playback restrictions",
    "Sanitize sharing links",
    "Save to watch later",
    "Seekbar",
    "Settings menu filter",
    "Shorts autoplay",
    "SponsorBlock",
    "Swipe controls",
    "Theme",
    "Video ads",
    "Video quality",
]

YT_MUSIC_INCLUDES = [
    "Change miniplayer color",
    "Change start page",
    "Crossfade",
    "Disable dislike redirection",
    "Downloads",
    "Enable exclusive audio playback",
    "Enable forced miniplayer",
    "Force original audio",
    "Hide ads",
    "Hide buttons",
    "Hide filter bar",
    "Hide flyout menu components",
    "Hide layout components",
    "Hide music action buttons",
    "Miniplayer previous and next buttons",
    "Navigation bar",
    "Play albums songs",
    "Playback speed",
    "Remove background playback restrictions",
    "Sanitize sharing links",
    "Settings menu filter",
    "SponsorBlock",
    "Theme",
    "Third-party lyrics",
]

MICROG_EXTRAS = [
    "GmsCore support",
    "PoToken provider",
    "Spoof video streams",
]

PATCH_TABLE: dict[str, dict[str, list[str]]] = {
    "youtube": {
        "base": YOUTUBE_INCLUDES,
        "microg": MICROG_EXTRAS + YOUTUBE_INCLUDES,
    },
    "music": {
        "base": YT_MUSIC_INCLUDES,
        "microg": MICROG_EXTRAS + YT_MUSIC_INCLUDES,
    },
}


def build_apks(latest_version: Version, app):
    apk = "big_file_merged.apk"
    patches = "bins/patches.mpp"
    cli = "bins/morphe-cli.jar"

    table = PATCH_TABLE[app.key]
    v = latest_version.version

    patch_apk(
        cli,
        patches,
        apk,
        includes=table["base"],
        out=f"{app.prefix}-morphe-v{v}.apk",
    )

    patch_apk(
        cli,
        patches,
        apk,
        includes=table["microg"],
        out=f"{app.prefix}-microg-morphe-v{v}.apk",
    )
