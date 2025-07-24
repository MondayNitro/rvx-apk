from dataclasses import dataclass
from typing import cast
from bs4 import BeautifulSoup, Tag
from utils import download, get_browser_session

session = get_browser_session()


@dataclass
class Version:
    version: str
    link: str


@dataclass
class Variant:
    is_bundle: bool
    link: str
    arcithecture: str


@dataclass
class App:
    name: str
    link: str


class FailedToFindElement(Exception):
    def __init__(self, message=None) -> None:
        self.message = (
            f"Failed to find element{' ' + message if message is not None else ''}"
        )
        super().__init__(self.message)


class FailedToFetch(Exception):
    def __init__(self, url=None) -> None:
        self.message = f"Failed to fetch{' ' + url if url is not None else ''}"
        super().__init__(self.message)


def get_versions(url: str) -> list[Version]:
    response = session.get(url)
    if response.status_code != 200:
        raise FailedToFetch(f"{url}: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    versions = soup.find("div", attrs={"class": "listWidget"})

    out: list[Version] = []
    if versions:
        for versionRow in cast(Tag, versions).findChildren("div", recursive=False)[1:]:
            version = versionRow.find("span", {"class": "infoSlide-value"})
            if version is None:
                continue

            version_str = version.string.strip()
            link = f"https://www.apkmirror.com{versionRow.find('a')['href']}"
            out.append(Version(version=version_str, link=link))

    return out


def download_apk(variant: Variant):
    """Download APK from the variant link"""
    url = variant.link
    response = session.get(url)
    if response.status_code != 200:
        raise FailedToFetch(url)

    soup = BeautifulSoup(response.content, "html.parser")
    download_button = soup.find("a", {"class": "downloadButton"})
    if download_button is None:
        raise FailedToFindElement("Download button")

    download_page_link = f"https://www.apkmirror.com{download_button['href']}"
    download_page = session.get(download_page_link)
    if download_page.status_code != 200:
        raise FailedToFetch(download_page_link)

    download_soup = BeautifulSoup(download_page.content, "html.parser")
    direct_link_tag = download_soup.find("a", {"rel": "nofollow"})
    if direct_link_tag is None:
        raise FailedToFindElement("download link")

    direct_link = f"https://www.apkmirror.com{direct_link_tag['href']}"
    print(f"Direct link: {direct_link}")

    download(direct_link, "big_file.apkm", session=session)


def get_variants(version: Version) -> list[Variant]:
    url = version.link
    response = session.get(url)
    if response.status_code != 200:
        raise FailedToFetch(url)

    soup = BeautifulSoup(response.content, "html.parser")
    table_div = soup.find("div", {"class": "table"})
    if table_div is None:
        raise FailedToFindElement("variants table")

    rows = cast(Tag, table_div).findChildren("div", recursive=False)[1:]

    variants: list[Variant] = []
    for row in rows:
        cells = row.findChildren("div", {"class": "table-cell"}, recursive=False)
        if len(cells) < 2:
            continue

        is_bundle_tag = row.find("span", {"class": "apkm-badge"})
        is_bundle = (
            is_bundle_tag and is_bundle_tag.string.strip().upper() == "BUNDLE"
        )

        architecture = cells[1].string.strip()
        link_element = row.find("a", {"class": "accent_color"})
        if link_element is None:
            continue

        link = f"https://www.apkmirror.com{link_element['href']}"
        variants.append(Variant(is_bundle=is_bundle, link=link, arcithecture=architecture))

    return variants
