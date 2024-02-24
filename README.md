# git-pr-helper

[![license](https://img.shields.io/badge/license-MIT-green)](https://github.com/Grub4K/git-pr-helper/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Git subcommand to aid with GitHub PRs interaction

_**NOTE**_: While this software is still very early in development, it should already be useful.
Don't expect speedy execution or good error handling for now though.

## Installation
For now, you have to install from git, e.g. `pipx install git+https://github.com/Grub4K/git-pr-helper.git`, and ensure its in `PATH`.

For easier and more convenient usage, you should create a git alias as well: `git config --global alias.pr "!git-pr-helper"`.
After this you can invoke it conveniently via `git pr ...`. Use `git pr help` to access the help instead of `--help`.

## How does it work
GitHub provides `refs/pull/*/head`, which we can use to get each PR; these are read only though, so maintainers or even the original authors cannot push to it.
To be able to push, we store the actual upstream pr remote in the branch description, and provide it explicitly: `git push git@github.com:user/repo.git HEAD:branch`.

Additionally, GitHub provides `refs/pull/*/merge` for all open PRs.
These can be used to determine if local PR branches can be removed (`prune`).

## Improvements
These are in order of relevance
- [ ] Error handling
- [ ] Add a way to manage branch description
- [ ] Use a simpler format for the branch description
- [ ] Better input and output helpers and wrappers
- [ ] Caching and lazy execution
- [ ] Automated release CI
- [ ] Do not hardcode `github.com`
