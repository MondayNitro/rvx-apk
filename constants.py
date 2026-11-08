import os

REPO = os.environ.get("GITHUB_REPOSITORY")
if REPO is None:
    raise EnvironmentError("GITHUB_REPOSITORY is not set")
