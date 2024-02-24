"""prune PRs that are merged or closed"""

from __future__ import annotations

import argparse
import typing
from collections import defaultdict

import rich.text

from git_pr_helper import styles
from git_pr_helper.utils import git

if typing.TYPE_CHECKING:
    import rich.console


def configure_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--dry",
        action="store_true",
        help="do not remove, only list what would be removed",
    )
    parser.add_argument(
        "--soft",
        action="store_true",
        help="use -d instead of -D when deleting the branch",
    )


def run(console: rich.console.Console, args: argparse.Namespace):
    remotes = defaultdict(set)
    lines = git(
        "for-each-ref",
        "--format",
        "%(refname:strip=-1) %(upstream:remotename)",
        "refs/heads/pr/*",
    )
    for line in lines:
        pr, _, remote = line.partition(" ")
        remotes[remote].add(pr)

    to_remove = []
    for remote, prs in remotes.items():
        lines = git("ls-remote", remote, "refs/pull/*/merge")
        to_remove.extend(prs.difference(line.rsplit("/", 2)[1] for line in lines))

    branches_to_remove = [f"pr/{pr_number}" for pr_number in to_remove]
    if args.dry:
        text = "Would remove: "
    else:
        text = "Pruned branches: "
        git("branch", "-d" if args.soft else "-D", *branches_to_remove)

    console.print(
        rich.text.Text.assemble(
            text,
            rich.text.Text(", ").join(
                rich.text.Text(branch, style=styles.ACCENT)
                for branch in branches_to_remove
            ),
        )
    )
    return 0
