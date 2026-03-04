import os
import shutil
import sys
import requests
import subprocess
import cloudscraper
from functools import lru_cache
from constants import HEADERS


@lru_cache(maxsize=1)
def get_browser_session() -> requests.Session:
    scraper = cloudscraper.create_scraper()
    scraper.headers.update(HEADERS.copy())  # avoid mutating shared constants
    return scraper


def panic(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def download(link: str, out: str, session: requests.Session | None = None) -> None:
    if os.path.exists(out):
        print(f"{out} already exists, skipping download")
        return

    sess = session or get_browser_session()
    r = sess.get(link, stream=True)
    try:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    finally:
        r.close()


def run_command(command: list[str]) -> None:
    cmd = subprocess.run(command, capture_output=True, text=True)
    try:
        cmd.check_returncode()
    except subprocess.CalledProcessError:
        print("Command failed:")
        print("STDOUT:", cmd.stdout)
        print("STDERR:", cmd.stderr)
        sys.exit(1)


def merge_apk(path: str) -> None:
    subprocess.run(
        ["java", "-jar", "./bins/apkeditor.jar", "m", "-i", path],
        check=True,
    )


def patch_apk(
    cli: str,
    patches: str,
    apk: str,
    includes: list[str] | None = None,
    excludes: list[str] | None = None,
    out: str | None = None,
) -> None:
    command = [
        "java",
        "-jar",
        cli,
        "patch",
        "-f",
        "--exclusive",
        "--purge",
        "--unsigned",
        "--legacy-options=options.json",
        "-p",
        patches,
    ]

    if includes:
        for i in includes:
            command += ["-e", i]

    if excludes:
        for e in excludes:
            command += ["-d", e]

    command.append(apk)

    subprocess.run(command, check=True)

    if out is not None:
        cli_output = f"{apk.removesuffix('.apk')}-patched.apk"
        if os.path.exists(out):
            os.unlink(out)
        shutil.move(cli_output, out)


def publish_release(tag: str, files: list[str], message: str) -> None:
    key = os.environ.get("GH_TOKEN")
    if not key:
        raise EnvironmentError("GH_TOKEN is not set")

    if not files:
        raise ValueError("Files list must have at least one item")

    command = ["gh", "release", "create", "--latest", tag, "--notes", message, *files]
    subprocess.run(command, env=os.environ.copy(), check=True)