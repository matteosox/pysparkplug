#!/usr/bin/env python3

import os

from github import Auth, Github
from packaging.version import Version

import pysparkplug


def main() -> None:
    auth = Auth.Token(os.environ["GITHUB_TOKEN"])
    github = Github(auth=auth)
    repo = github.get_repo("matteosox/pysparkplug")
    tag = f"v{pysparkplug.__version__}"
    name = pysparkplug.__version__
    prerelease = Version(pysparkplug.__version__).is_prerelease
    repo.create_git_release(
        tag=tag,
        name=name,
        draft=True,
        generate_release_notes=True,
        prerelease=prerelease,
    )


if __name__ == "__main__":
    main()
