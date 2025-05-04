# Aquarion AI - Text To Speech (TTS) Library

Experiment in creating a scalable local AI voice chat bot.

[![Static Badge](https://img.shields.io/badge/Part_of-Aquarion_AI-blue)](https://github.com/aquarion-ai)

<!-- markdownlint-disable MD013 -->
<!--
[![PyPI - Version](https://img.shields.io/pypi/v/aquarion-libtts.svg)](https://pypi.org/project/aquarion-libtts)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aquarion-libtts.svg)](https://pypi.org/project/aquarion-libtts)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/aquarion-libtts)](https://pypi.org/project/aquarion-libtts)
[![PyPI - Types](https://img.shields.io/pypi/types/aquarion-libtts)](https://pypi.org/project/aquarion-libtts)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/aquarion-libtts)](https://pypi.org/project/aquarion-libtts)
[![PyPI - Format](https://img.shields.io/pypi/format/aquarion-libtts)](https://pypi.org/project/aquarion-libtts)
[![PyPI - Status](https://img.shields.io/pypi/status/aquarion-libtts)](https://pypi.org/project/aquarion-libtts)
[![PyPI - License](https://img.shields.io/pypi/l/aquarion-libtts)](https://pypi.org/project/aquarion-libtts)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/aquarion-libtts)](https://pypi.org/project/aquarion-libtts)
-->
<!-- markdownlint-enable MD013 -->

[![build](https://github.com/aquarion-ai/aquarion-libtts/actions/workflows/build.yml/badge.svg)](https://github.com/aquarion-ai/aquarion-libtts/actions/workflows/build.yml)
[![Test Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/justkrys/079b402971d82c07d05c74f37c57b088/raw/aquarion-ai_aquarion-libtts__main__test.json)](https://github.com/aquarion-ai/aquarion-libtts/actions)
[![Acceptance Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/justkrys/079b402971d82c07d05c74f37c57b088/raw/aquarion-ai_aquarion-libtts__main__accept.json)](https://github.com/aquarion-ai/aquarion-libtts/actions)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/aquarion-ai/aquarion-libtts)](https://github.com/aquarion-ai/aquarion-libtts)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-closed/aquarion-ai/aquarion-libtts)](https://github.com/aquarion-ai/aquarion-libtts)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/aquarion-ai/aquarion-libtts)](https://github.com/aquarion-ai/aquarion-libtts)
[![GitHub last commit](https://img.shields.io/github/last-commit/aquarion-ai/aquarion-libtts)](https://github.com/aquarion-ai/aquarion-libtts)
<!-- markdownlint-disable MD013 -->
<!--
[![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/aquarion-ai/aquarion-libtts/total)](https://github.com/aquarion-ai/aquarion-libtts)
[![GitHub Release Date](https://img.shields.io/github/release-date/aquarion-ai/aquarion-libtts)](https://github.com/aquarion-ai/aquarion-libtts)
-->
<!-- markdownlint-enable MD013 -->

[![GitHub Repo stars](https://img.shields.io/github/stars/aquarion-ai/aquarion-libtts)](https://github.com/aquarion-ai/aquarion-libtts)
[![GitHub watchers](https://img.shields.io/github/watchers/aquarion-ai/aquarion-libtts)](https://github.com/aquarion-ai/aquarion-libtts)
[![GitHub forks](https://img.shields.io/github/forks/aquarion-ai/aquarion-libtts)](https://github.com/aquarion-ai/aquarion-libtts)

[![Built with Devbox](https://www.jetify.com/img/devbox/shield_galaxy.svg)](https://www.jetify.com/devbox/docs/contributor-quickstart/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

-----

## Table of Contents

- [About](#about)
  - [About Aquarion AI](#about-aquarion-ai)
  - [About this Repository](#about-this-repository)
  - [Disclaimer](#disclaimer)
  - [License](#license)
- [User Information](#user-information)
- [Developer Information](#developer-information)
  - [Development Standards](#development-standards)
  - [Developer Installation](#developer-installation)
    - [Developer Installation Details](#developer-installation-details)

## About

### About Aquarion AI

The goal of this project is to create an LLM-based voice chat bot / assistant, but to
built it in such a way that is can be scaled down to a single desktop app, all the way
up to a distributed multi-server, horizontally scalable system.  Also, desired is a
taking head / avatar who's mouth moves with the speech.  Lastly, it should all run
locally / offline, even in an air gapped environment.  Oh, and it should be modular
enough to support multiple alternate STT, LLM and TTS models/engines/options.

### About this Repository

The repository contains the library of Text To Speech (TTS) backend components for
Aquarion AI.

### Disclaimer

While this project is FOSS and you are welcome to use it (if it ever becomes something
usable), know that I am making this for myself. So do not expect any kind of support or
updates or maintenance or longevity.  Caveat Emptor.

### License

`aquarion-libtts` is distributed under the terms of the
[AGPL-3.0-only](https://spdx.org/licenses/AGPL-3.0-only.html) license.

## User Information

For user documentation, see the
[aquarion-docs](https://github.com/aquarion-ai/aquarion-docs) project.

## Developer Information

### Development Standards

This project follows the following standard practices:

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) for
  commit messages.
- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) for versioning.
- [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) for the changelog.

### Developer Installation

1. Clone this repository.

1. Install [Devbox](https://www.jetify.com/docs/devbox/installing_devbox/)

1. Run:

   ```console
   devbox shell
   init
   check dep all
   check push
   check --help
   ```

#### Developer Installation Details

- Devbox is a tool for creating per-project development environments using Nix.  It is
  used in this project for non-Python dev tools and bootstrapping.
- On first run, `devbox shell` will download and install all the needed system tools
  for the environment
- On the first run, `init` will download and install the base Python version, needed
  commands, hooks, etc.
- pre-commit is a tool for running certain checks and fixes on the code before commits
  and/or pushes.  `check dep all` runs those hooks on all files.
- **NOTE:** No commit, push or pull request should or will be accepted unless all
  pre-commit and pre-push hooks pass.  No exceptions!
- Hatch is a tool for managing dependencies, builds, virtual environments and Python
  versions, as well as running tests, formatting, linting and typechecking.
- The `check` command calls Hatch to perform common tasks, while also making it easier
  to do so.
- `check push` runs all common tasks, like type checking, formatting, linting, unit
   tests, acceptance tests, coverage checks, etc.
- On first run, `check push` will also download and install several files, etc.
- The `check` command has several sub-commands to help you while developing.  Check it
  out. :smile_cat:
