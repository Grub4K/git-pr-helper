"""setup prs for a specific remote"""

from __future__ import annotations

import re
import typing

import rich.text

from git_pr_helper import styles
from git_pr_helper.utils import git

if typing.TYPE_CHECKING:
    import argparse

    import rich.console


def configure_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "remote",
        nargs="?",
        default="origin",
        help="the remote to setup PRs on",
    )


def run(console: rich.console.Console, args: argparse.Namespace):
    section = f"remote.{args.remote}.fetch"
    value = f"+refs/pull/*/head:refs/remotes/{args.remote}/pr/*"
    git("config", "--replace-all", section, value, f"^{re.escape(value)}$|^$")
    console.print(
        rich.text.Text.assemble(
            "Successfully set up: ",
            (args.remote, styles.ACCENT),
        )
    )
    return 0
