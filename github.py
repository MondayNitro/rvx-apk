from dataclasses import dataclass
from urllib.parse import quote

import requests

REQUEST_TIMEOUT_SECONDS = 30


@dataclass
class Asset:
    browser_download_url: str
    name: str


@dataclass
class GithubRelease:
    tag_name: str
    html_url: str
    assets: list[Asset]


def _to_github_release(release: dict) -> GithubRelease:
    assets = [
        Asset(browser_download_url=a["browser_download_url"], name=a["name"])
        for a in release["assets"]
    ]
    return GithubRelease(
        tag_name=release["tag_name"], html_url=release["html_url"], assets=assets
    )


def get_release_by_tag(repo: str, tag: str) -> GithubRelease | None:
    url = f"https://api.github.com/repos/{repo}/releases/tags/{quote(tag, safe='')}"
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return _to_github_release(response.json())
