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


def run(console: rich.console.Console, args: argparse.Namespace):
    current_hash = git("rev-list", "-n", "1", "HEAD")[0]
    head_ref, _, current_remote_ref = git(
        "for-each-ref",
        "--format=%(refname) %(upstream)",
        "--points-at",
        current_hash,
        "refs/heads/**",
    )[0].partition(" ")
    current_branch = head_ref.removeprefix("refs/heads/")
    current_remote, _, remote_ref = (
        current_remote_ref.partition("/")[2].partition("/")[2].partition("/")
    )
    remote_ref = remote_ref.partition("/")[2]

    config = dict(read_pr_branch_infos())
    pr_branch_info = config.get(current_branch)
    if not pr_branch_info:
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
    git("fetch", "--all", "--update-head-ok", current_remote, ref_spec)
    return 0
