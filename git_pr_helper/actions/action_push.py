"""push a ref to the PRs origin branch"""

from __future__ import annotations

import argparse
import typing

import rich.text

from git_pr_helper import styles
from git_pr_helper.utils import git
from git_pr_helper.utils import read_pr_branch_infos

if typing.TYPE_CHECKING:
    import rich.console


# Workaround for `argparse.REMAINDER`
PARSER_ARGS = {"prefix_chars": "`"}


def configure_parser(parser: argparse.ArgumentParser):
    parser.add_argument(dest="remaining", nargs=argparse.REMAINDER)


def parse_ref_line(line: str):
    head_ref, _, current_remote_ref = line.partition(" ")
    current_branch = head_ref.removeprefix("refs/heads/")
    current_remote, _, remote_ref = current_remote_ref.removeprefix(
        "refs/remotes/"
    ).partition("/")
    remote_ref = remote_ref.partition("/")[2]

    return current_branch, current_remote, remote_ref


def run(console: rich.console.Console, args: argparse.Namespace):
    config = dict(read_pr_branch_infos())
    current_hash = git("rev-list", "-n", "1", "HEAD")[0]
    lines = git(
        "for-each-ref",
        "--format=%(refname) %(upstream)",
        "--points-at",
        current_hash,
        "refs/heads/**",
    )

    for line in lines:
        current_branch, current_remote, remote_ref = parse_ref_line(line)
        pr_branch_info = config.get(current_branch)
        if pr_branch_info:
            break
    else:
        console.print(
            rich.text.Text.assemble(
                ("error", styles.ERROR),
                ": current branch is not a PR",
            )
        )
        return 1

    # TODO(Grub4K): lazy if already up to date
    git("push", *args.remaining, pr_branch_info.remote, f"HEAD:{pr_branch_info.branch}")
    ref_spec = f"refs/pull/{remote_ref}/head:pr/{remote_ref}"
    git("fetch", "--update-head-ok", current_remote, ref_spec)
    return 0
