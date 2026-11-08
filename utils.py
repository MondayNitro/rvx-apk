import os
import shutil
import subprocess
import sys
import glob
import requests

_scraper = None

def get_scraper():
    global _scraper
    if _scraper is None:
        from curl_cffi import requests as cffi_requests
        # impersonate sets matching TLS fingerprint + headers, so don't override User-Agent
        _scraper = cffi_requests.Session(impersonate="chrome", timeout=60)
    return _scraper


def panic(message: str):
    print(message, file=sys.stderr)
    exit(1)


def download(link, out, headers=None, use_scraper=False):
    dir_name = os.path.dirname(out)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    if os.path.exists(out):
        print(f"{out} already exists skipping download")
        return

    if use_scraper:
        print(f"Downloading with scraper: {link}")

    session = get_scraper() if use_scraper else requests

    # https://www.slingacademy.com/article/python-requests-module-how-to-download-files-from-urls/#Streaming_Large_Files
    r = session.get(link, stream=True, headers=headers)
    try:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    finally:
        r.close()

def run_command(command: list[str]):
    cmd = subprocess.run(command, capture_output=True, text=True)

    try:
        cmd.check_returncode()
    except subprocess.CalledProcessError:
        print(cmd.stdout)
        print(cmd.stderr)
        exit(1)


def merge_apk(path: str):
    subprocess.run(
        ["java", "-jar", "./bins/apkeditor.jar", "m", "-extractNativeLibs", "true", "-i", path]
    ).check_returncode()


def patch_apk(
    cli: str,
    patches: str,
    apk: str,
    includes: list[str] | None = None,
    excludes: list[str] | None = None,
    out: str | None = None,
):
    command = [
        "java",
        "-jar",
        cli,
        "patch",
        "--exclusive",
        "-f",
        "-p",
        patches,
        "--options-file=options.json",
        "--unsigned",
    ]

    if includes is not None:
        for i in includes:
            command.append("-e")
            command.append(i)

    if excludes is not None:
        for e in excludes:
            command.append("-d")
            command.append(e)

    command.append(apk)

    subprocess.run(command).check_returncode()

    # Morphe output path
    if out is not None:
        apk_dir = os.path.splitext(apk)[0]
        patched_apk = glob.glob(os.path.join(apk_dir, "*.apk"))

        if not patched_apk:
            raise FileNotFoundError(f"No APK found in {apk_dir}")
        
        cli_output = patched_apk[0]
        print(f"Morphe output: {cli_output}")

        if os.path.exists(out):
            os.unlink(out)
            
        shutil.move(cli_output, out)


def publish_release(tag: str, files: list[str], message: str, title = ""):
    key = os.environ.get("GITHUB_TOKEN")
    if key is None:
        raise Exception("GITHUB_TOKEN is not set")

    command = ["gh", "release", "create", "--latest", tag, "--notes", message, "--title", title]

    if len(files) == 0:
        raise Exception("Files should have atleast one item")

    for file in files:
        command.append(file)

    subprocess.run(command, env=os.environ.copy()).check_returncode()
