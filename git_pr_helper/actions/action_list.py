"""list currently available pr branches"""

from __future__ import annotations

import dataclasses
import typing

import rich.box
import rich.table
import rich.text

from git_pr_helper.utils import abbreviate_remote
from git_pr_helper.utils import git
from git_pr_helper.utils import read_pr_branch_infos

if typing.TYPE_CHECKING:
    import argparse

    import rich.console


@dataclasses.dataclass
class BranchInfo:
    is_head: bool
    commit_hash: str
    local: str
    ahead_local: int
    remote: str
    ahead_remote: int
    real_remote: str
    real_branch: str
    description: str | None


def configure_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "pattern",
        nargs="?",
        help="optional pattern to filter for",
    )


def run(console: rich.console.Console, args: argparse.Namespace):
    branches: dict[str, BranchInfo] = {}
    pattern = args.pattern or "pr/*"

    pr_branch_infos = dict(read_pr_branch_infos(pattern))

    output_format = " ".join(
        [
            "%(if)%(HEAD)%(then)1%(else)0%(end)",
            "%(objectname)",
            "%(objectname:short)",
            "%(refname:strip=2)",
            "%(upstream:strip=2)",
        ]
    ).join(("%(if)%(upstream:short)%(then)", "%(end)"))
    items = git(
        "for-each-ref",
        "--omit-empty",
        f"--format={output_format}",
        f"refs/heads/{pattern}",
    )
    for item in items:
        head, commit_full, commit, local, remote = item.split(" ")
        ahead, _, behind = git(
            "rev-list",
            "--left-right",
            "--count",
            f"{commit_full}...{remote}",
        )[0].partition("\t")
        pr_branch_info = pr_branch_infos.get(local)
        if not pr_branch_info:
            continue
        branches[local] = BranchInfo(
            head == "1",
            commit,
            local,
            int(ahead),
            remote,
            int(behind),
            pr_branch_info.remote,
            pr_branch_info.branch,
            pr_branch_info.description[0] if pr_branch_info.description else None,
        )

    remote_config = git("config", "--get-regexp", "remote.*.url")
    remotes = {
        path.removeprefix("remote.").removesuffix(".url"): abbreviate_remote(remote)
        for path, remote in map(str.split, remote_config)
    }

    table = rich.table.Table(box=rich.box.SIMPLE)
    table.add_column("", style="bold green")
    table.add_column("commit", style="bright_yellow")
    table.add_column("local", style="bright_cyan")
    table.add_column("remote", style="bright_cyan")
    table.add_column("push")
    table.add_column("note", style="bright_white")

    for branch in branches.values():
        head = "*" if branch.is_head else " "
        local = rich.text.Text(branch.local)
        if branch.ahead_local:
            local.append(f" +{branch.ahead_local}", "green")
        remote_name, _, pr_number = branch.remote.split("/")
        remote = rich.text.Text("")
        remote.append(
            f"{remote_name}#{pr_number}",
            f"link https://github.com/{remotes[remote_name]}/pull/{pr_number}",
        )
        if branch.ahead_remote:
            remote.append(f" +{branch.ahead_remote}", "red")

        real_remote = abbreviate_remote(branch.real_remote)
        push = rich.text.Text.assemble(
            (real_remote, "bright_magenta"),
            " @ ",
            (branch.real_branch, "bright_cyan"),
        )

        table.add_row(head, branch.commit_hash, local, remote, push, branch.description)

    console.print(table)
    return 0
