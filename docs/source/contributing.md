# Contributing

<!--
    SPDX-FileCopyrightText: 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
    SPDX-License-Identifier: CC-BY-SA-4.0
-->

<!--
    aquarion-libtts documentation © 2025-present by Krys Lawrence is licensed under
    Creative Commons Attribution-ShareAlike 4.0 International. To view a copy of this
    license, visit <https://creativecommons.org/licenses/by-sa/4.0/>
-->

## Disclaimer

--8<--
README.md:disclaimer
--8<--

With that said, if you still want to try contributing, then nothing is stopping you.
And to that end (and for my future self), here is documented some helpful info on how
the project is put together and developed.

## Development Standards

This project follows the following standard practices:

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) for
  commit messages.

    - If using VS Code, then the
      [Conventional Commits](https://marketplace.visualstudio.com/items?itemName=vivaxy.vscode-conventional-commits)
      extension is recommended.

    - _If committing from the terminal, use `cz c` instead of `git commit`._

- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) for versioning.

- [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) for the changelog.

- [Make a README](https://www.makeareadme.com/) for the README

- [REUSE SOFTWARE](https://reuse.software/) for licence and copyright information.

- [Ruff](https://docs.astral.sh/ruff/) for Python code style.

- [Markdown](https://commonmark.org/) for docstrings and generated API documentation.
    - _(with enhancements for use with [mkdocs](https://www.mkdocs.org/) and various
      plugins.)_

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
  for comments and docstrings.

- [Behaviour Driven Development](https://en.wikipedia.org/wiki/Behavior-driven_development)
  for acceptance tests.

## Developer Installation

1. Update NVIDIA drivers. \
   _Currently testing against version 570._

1. Install [Devbox](https://www.jetify.com/docs/devbox/installing_devbox/). \
   _Currently testing against version 0.16.0._

1. Clone this repository.

1. Run:

   ```sh linenums="1"
   devbox shell
   init
   check push
   hatch build
   docs build
   check --help
   lang --help
   ```

### Installation Details

- Currently only CUDA is supported for GPU acceleration of TTS Models.  Though, CPU-only
  mode is also supported.

- [Devbox](https://www.jetify.com/devbox) is a tool for creating per-project development
  environments using [Nix](https://github.com/NixOS/nix) (not to be confused with
  NixOS).  It is used in this project for non-Python dev tools and bootstrapping.

- On first run, `devbox shell` will download and install all the needed system tools
  for the environment

- On the first run, `init` will download and install the base Python version, needed
  commands, hooks, etc.

- pre-commit is a tool for running certain checks and fixes on the code before commits
  and/or pushes.

- **NOTE:** No commit, push or pull request should or will be accepted unless all
  pre-commit and pre-push hooks pass.  No exceptions!

- Hatch is a tool for managing dependencies, builds, virtual environments and Python
  versions, as well as running tests, formatting, linting and typechecking.

- The `check` command calls Hatch to perform common tasks, while also making it easier
  to do so.

- `check push` runs all common tasks like pre-commit checks, type checks, formatting,
   linting, unit tests, acceptance tests, coverage checks, security checks, etc.

- On first run, `check push` will also download and install several files, etc.

- `hatch build` is how the source and wheel distributions are made.

- `docs build` is how to generate the documentation.

- The `check` command has several sub-commands to help you while developing.  Check it
  out. 😺

- The `lang` command is used to manage localization message catalogues, i.e. translation
  files.  It's good to check it out as well.

- You can run the Python REPL with `hatch run python`.

- You can enter the default virtual environment with `hatch shell`.

## What Tool Does What

Several of the development tools used in this project have overlapping capabilities.
This section is an attempt clarify which tool is used for which common task.

| Task                                      | Tool                                     |
| ----------------------------------------- | ---------------------------------------- |
| Install non-Python dev tools              | Devbox (NIX)                             |
| Install Python dev tools                  | The `init` script (uv)                   |
| Install base/minimum Python version       | The `init` script (uv)                   |
| Install extra Python versions for testing | The `check` script (Hatch)               |
| Install pre-commit hooks                  | The `init` script (pre-commit)           |
| Format code                               | The `check` script (Hatch, Ruff)         |
| Lint code                                 | The `check` script (Hatch, Ruff)         |
| Type check code                           | The `check` script (Hatch, mypy)         |
| Run tests                                 | The `check` script (Hatch, pytest)       |
| Run acceptance tests                      | The `check` script (Hatch, radish-bdd)   |
| Run code coverage checks                  | The `check` script (Hatch, coverage)     |
| Run pre-commit hooks manually             | The `check` script (pre-commit)          |
| Enter the default virtual environment     | Hatch                                    |
| Commit changes from the terminal          | Commitizen _(use `cz c`)_                |
| Report on last code coverage run          | The `report` script (coverage)           |
| Update version on a release               | Hatch                                    |
| Build distribution artifacts              | Hatch                                    |
| Add / update language translations        | The `lang` script (Hatch, babel)         |
| Generate the documentation                | The `docs` script (Hatch, Mkdocs)        |
| Pin project dependency versions           | uv                                       |
| Pin development dependency versions       | uv                                       |
| Format Markdown                           | pre-commit (markdownlint-cli2)           |
| Format YAML                               | pre-commit (yamlfmt)                     |
| Format JSON                               | pre-commit (pretty-format-json)          |
| Spell checking                            | pre-commit (codespell), `docs` (Mkdocs)  |
| Manage translations                       | The `lang` script (Hatch, Babel)         |
| Remove all venvs, tools, caches, etc.     | The `clean` script                       |
| Run CI pipeline                           | Github Actions (using the scripts above) |
