"""add a new pr branch or convert aan existing branch to one"""

from __future__ import annotations

import typing

import rich.text

from git_pr_helper import styles
from git_pr_helper.utils import PrBranchInfo
from git_pr_helper.utils import git
from git_pr_helper.utils import write_pr_branch_info

if typing.TYPE_CHECKING:
    import argparse

    import rich.console


def configure_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--prune",
        action="store_true",
        help="remove branches that have the same HEAD as the PR",
    )
    parser.add_argument(
        "pr",
        help="the pr to add, in the format <remote>#<number>",
    )


def run(console: rich.console.Console, args: argparse.Namespace):
    pr_remote, _, pr_number = args.pr.rpartition("#")
    if not pr_remote:
        pr_remote = "*"

    try:
        pr_number = str(int(pr_number))
    except ValueError:
        console.print(
            rich.text.Text.assemble(
                ("error", styles.ERROR),
                ": ",
                (pr_number, styles.ACCENT),
                " is not a number",
            )
        )
        return 1

    head_hashes = [
        line.partition(" ")[::2]
        for line in git(
            "for-each-ref",
            "--format=%(objectname) %(refname:strip=2)",
            f"refs/remotes/{pr_remote}/pr/{pr_number}",
        )
    ]
    if not head_hashes:
        console.print(
            rich.text.Text.assemble(
                ("error", styles.ERROR),
                ": did not find a matching pr",
            )
        )
        return 1
    elif len(head_hashes) > 1:
        console.print(
            rich.text.Text.assemble(
                ("error", styles.ERROR),
                ": found more than one PR: ",
                rich.text.Text(", ").join(
                    rich.text.Text(pr_remote.replace("/pr/", "#"), style=styles.ACCENT)
                    for _, pr_remote in head_hashes
                ),
            )
        )
        return 1
    head_hash, pr_remote = head_hashes[0]
    pr_remote = pr_remote.partition("/")[0]

    branches = git(
        "for-each-ref",
        "--points-at",
        head_hash,
        "--exclude",
        "refs/remotes/**/pr/*",
        "--format",
        "%(refname:strip=2)",
        "refs/remotes/**",
    )
    if len(branches) > 1:
        console.print(
            rich.text.Text.assemble(
                ("More than one branch found", styles.ERROR),
                ": ",
                rich.text.Text(", ").join(
                    rich.text.Text(branch, style=styles.ACCENT) for branch in branches
                ),
            )
        )
        branches = []

    if branches:
        remote, _, branch = branches[0].partition("/")

    else:
        console.show_cursor()
        info = console.input(
            rich.text.Text.assemble(
                "Enter branch info (",
                ("<user>/<repo>", styles.ACCENT),
                ":",
                ("<branch>", styles.ACCENT),
                "): ",
            )
        )
        console.show_cursor(False)
        remote, _, branch = info.partition(":")
        if "/" in remote:
            remote = f"git@github.com:{remote}.git"

    name = f"pr/{pr_number}"
    git("switch", "-c", name, "--track", f"{pr_remote}/{name}")
    write_pr_branch_info(name, PrBranchInfo(remote, branch, []))

    if args.prune:
        branches = git(
            "for-each-ref",
            "--points-at",
            head_hash,
            "--exclude",
            "refs/heads/**/pr/*",
            "--format",
            "%(refname:strip=2)",
            "refs/heads/**",
        )
        if branches:
            git("branch", "-D", branch)
            console.print(
                rich.text.Text.assemble(
                    "Pruned branches: ",
                    rich.text.Text(", ").join(
                        rich.text.Text(branch, style=styles.ACCENT)
                        for branch in branches
                    ),
                )
            )

    return 0
