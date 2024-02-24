from __future__ import annotations

import dataclasses
import fnmatch
import subprocess

PR_BRANCH_PREFIX = "!!git pr"


def abbreviate_remote(remote: str):
    return remove_around(remote, "git@github.com:", ".git")


def remove_around(data: str, before: str, after: str):
    return data.removeprefix(before).removesuffix(after)


def git(*args: str):
    null = False

    for arg in args:
        if arg == "--null":
            null = True
            break
        if arg == "--":
            break

    command = ["git", *args]
    output = subprocess.check_output(command, text=True)
    if null:
        return output.split("\x00")
    return output.splitlines()


@dataclasses.dataclass
class PrBranchInfo:
    remote: str
    branch: str
    description: list[str]


def read_pr_branch_infos(pattern: str | None = None):
    if pattern:
        re_pattern = remove_around(fnmatch.translate(pattern), "(?s:", ")\\Z")
    else:
        re_pattern = "[^.]*"
    filter_pattern = rf"branch\.{re_pattern}\.description"

    descriptions = git("config", "--null", "--get-regexp", filter_pattern)
    for description in descriptions:
        name, _, description = description.partition("\n")
        if not description.startswith(PR_BRANCH_PREFIX):
            continue
        name = remove_around(name, "branch.", ".description")
        _, remote, branch, *description = description.split("\n")
        yield name, PrBranchInfo(remote, branch, description)


def write_pr_branch_info(name: str, info: PrBranchInfo):
    description = "\n".join(
        [
            PR_BRANCH_PREFIX,
            info.remote,
            info.branch,
            *info.description,
        ]
    )
    git("config", "--null", f"branch.{name}.description", description)
