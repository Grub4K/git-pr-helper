from __future__ import annotations

import inspect
import subprocess
import sys

from rich.console import Console

import git_pr_helper.actions


def _main():
    import argparse

    root_parser = argparse.ArgumentParser("git pr", add_help=False)
    # root_parser.add_argument(
    #     "-C",
    #     dest="path",
    #     metavar="<path>",
    #     help="set the base path for the git repository",
    # )
    subparsers = root_parser.add_subparsers(title="action", dest="action")

    ALL_ACTIONS = {
        name.removeprefix("action_"): getattr(git_pr_helper.actions, name)
        for name in dir(git_pr_helper.actions)
        if name.startswith("action_")
    }

    parsers = {}
    for name, module in ALL_ACTIONS.items():
        parser_args = getattr(module, "PARSER_ARGS", None) or {}
        parser = subparsers.add_parser(
            name, **parser_args, add_help=False, help=inspect.getdoc(module)
        )
        module.configure_parser(parser)
        parsers[name] = parser

    parser = subparsers.add_parser("help", help="show this help message and exit")
    parser.add_argument(
        "subcommand",
        nargs="?",
        choices=[*ALL_ACTIONS, "help"],
        help="the subcommand to get help for",
    )
    parsers["help"] = parser

    args = root_parser.parse_args()
    if args.action is None:
        root_parser.error("need to provide an action")
    elif args.action == "help":
        parser = parsers[args.subcommand] if args.subcommand else root_parser
        print(parser.format_help())
        exit(0)

    runner = ALL_ACTIONS[args.action].run

    console = Console()
    console.show_cursor(False)
    try:
        sys.exit(runner(console, args))

    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)

    finally:
        console.show_cursor()


def main():
    try:
        _main()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
