from dataclasses import dataclass
from typing import cast
from bs4 import BeautifulSoup, Tag
import requests

from utils import download, get_browser_session

BASE_URL = "https://www.apkmirror.com"


def get_session() -> requests.Session:
    return get_browser_session()


@dataclass
class Version:
    version: str
    link: str


@dataclass
class Variant:
    is_bundle: bool
    link: str
    architecture: str


@dataclass
class App:
    name: str
    link: str


class FailedToFindElement(Exception):
    def __init__(self, message: str | None = None) -> None:
        suffix = f" {message}" if message else ""
        super().__init__(f"Failed to find element{suffix}")


class FailedToFetch(Exception):
    def __init__(self, url: str | None = None) -> None:
        suffix = f" {url}" if url else ""
        super().__init__(f"Failed to fetch{suffix}")


def get_versions(url: str) -> list[Version]:
    session = get_session()
    r = session.get(url)
    try:
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
    finally:
        r.close()

    versions_div = soup.find("div", class_="listWidget")
    if not versions_div:
        return []

    out: list[Version] = []
    rows = cast(Tag, versions_div).find_all("div", recursive=False)[1:]

    for row in rows:
        version_tag = row.find("span", class_="infoSlide-value")
        link_tag = row.find("a")

        if not version_tag or not link_tag or not link_tag.get("href"):
            continue

        out.append(
            Version(
                version=version_tag.get_text(strip=True),
                link=f"{BASE_URL}{link_tag['href']}",
            )
        )

    return out


def download_apk(variant: Variant) -> None:
    session = get_session()

    r = session.get(variant.link)
    try:
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
    finally:
        r.close()

    download_button = soup.find("a", class_="downloadButton")
    if download_button is None or not download_button.get("href"):
        raise FailedToFindElement("download button")

    download_page_link = f"{BASE_URL}{download_button['href']}"

    r = session.get(download_page_link)
    try:
        r.raise_for_status()
        download_soup = BeautifulSoup(r.content, "html.parser")
    finally:
        r.close()

    direct_link_tag = download_soup.find("a", rel="nofollow")
    if direct_link_tag is None or not direct_link_tag.get("href"):
        raise FailedToFindElement("direct download link")

    direct_link = f"{BASE_URL}{direct_link_tag['href']}"
    print(f"Direct link: {direct_link}")

    download(direct_link, "big_file.apkm", session=session)


def get_variants(version: Version) -> list[Variant]:
    session = get_session()

    r = session.get(version.link)
    try:
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
    finally:
        r.close()

    table_div = soup.find("div", class_="table")
    if table_div is None:
        raise FailedToFindElement("variants table")

    rows = cast(Tag, table_div).find_all("div", recursive=False)[1:]
    variants: list[Variant] = []

    for row in rows:
        cells = row.find_all("div", class_="table-cell", recursive=False)
        if len(cells) < 2:
            continue

        architecture = cells[1].get_text(strip=True)

        is_bundle_tag = row.find("span", class_="apkm-badge")
        is_bundle = (
            bool(is_bundle_tag)
            and is_bundle_tag.get_text(strip=True).upper() == "BUNDLE"
        )

        link_tag = row.find("a", class_="accent_color")
        if not link_tag or not link_tag.get("href"):
            continue

        variants.append(
            Variant(
                is_bundle=is_bundle,
                architecture=architecture,
                link=f"{BASE_URL}{link_tag['href']}",
            )
        )

    return variants