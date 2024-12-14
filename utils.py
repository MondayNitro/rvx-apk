import os
import shutil
import requests
import subprocess
import sys
from github import get_last_build_version


def panic(message: str):
    print(message, file=sys.stderr)
    exit(1)


def download(link, out, headers=None):
    if os.path.exists(out):
        print(f"{out} already exists skipping download")
        return

    # https://www.slingacademy.com/article/python-requests-module-how-to-download-files-from-urls/#Streaming_Large_Files
    with requests.get(link, stream=True, headers=headers) as r:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def run_command(command: list[str]):
    cmd = subprocess.run(command, capture_output=True, shell=True)

    try:
        cmd.check_returncode()
    except subprocess.CalledProcessError:
        print(cmd.stdout)
        print(cmd.stderr)
        exit(1)


def merge_apk(path: str):
    subprocess.run(
        ["java", "-jar", "./bins/apkeditor.jar", "m", "-i", path]
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
        "-p",
        patches,
        "--unsigned",
        "--exclusive",
        "--legacy-options=options.json",
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

    # remove -patched from the apk to match out
    if out is not None:
        cli_output = f"{str(apk).removesuffix(".apk")}-patched.apk"
        if os.path.exists(out):
            os.unlink(out)
        shutil.move(cli_output, out)


def publish_release(tag: str, files: list[str], message: str):
    key = os.environ.get("GH_TOKEN")
    if key is None:
        raise Exception("GH_TOKEN is not set")

    command = ["gh", "release", "create", "--latest", tag, "--notes", message]

    if len(files) == 0:
        raise Exception("Files should have atleast one item")

    for file in files:
        command.append(file)

    subprocess.run(command, env=os.environ.copy()).check_returncode()
