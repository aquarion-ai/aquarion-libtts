# Aquarion AI - Text To Speech (TTS) Library

Experiment in creating a scalable local AI voice chat bot.

[![Static Badge](https://img.shields.io/badge/Part_of-Aquarion_AI-blue)](https://github.com/aquarion-ai)

<!-- [![PyPI - Version](https://img.shields.io/pypi/v/aquarion-tts.svg)](https://pypi.org/project/aquarion-tts)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aquarion-tts.svg)](https://pypi.org/project/aquarion-tts)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/aquarion-tts)](https://pypi.org/project/aquarion-tts)
[![PyPI - Types](https://img.shields.io/pypi/types/aquarion-tts)](https://pypi.org/project/aquarion-tts)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/aquarion-tts)](https://pypi.org/project/aquarion-tts)
[![PyPI - Format](https://img.shields.io/pypi/format/aquarion-tts)](https://pypi.org/project/aquarion-tts)
[![PyPI - Status](https://img.shields.io/pypi/status/aquarion-tts)](https://pypi.org/project/aquarion-tts)
[![PyPI - License](https://img.shields.io/pypi/l/aquarion-tts)](https://pypi.org/project/aquarion-tts)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/aquarion-tts)](https://pypi.org/project/aquarion-tts) -->

[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/aquarion-ai/aquarion-tts)](https://github.com/aquarion-ai/aquarion-tts)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-closed/aquarion-ai/aquarion-tts)](https://github.com/aquarion-ai/aquarion-tts)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/aquarion-ai/aquarion-tts)](https://github.com/aquarion-ai/aquarion-tts)
[![GitHub last commit](https://img.shields.io/github/last-commit/aquarion-ai/aquarion-tts)](https://github.com/aquarion-ai/aquarion-tts)
<!-- [![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/aquarion-ai/aquarion-tts/total)](https://github.com/aquarion-ai/aquarion-tts)
[![GitHub Release Date](https://img.shields.io/github/release-date/aquarion-ai/aquarion-tts)](https://github.com/aquarion-ai/aquarion-tts) -->

[![GitHub Repo stars](https://img.shields.io/github/stars/aquarion-ai/aquarion-tts)](https://github.com/aquarion-ai/aquarion-tts)
[![GitHub watchers](https://img.shields.io/github/watchers/aquarion-ai/aquarion-tts)](https://github.com/aquarion-ai/aquarion-tts)
[![GitHub forks](https://img.shields.io/github/forks/aquarion-ai/aquarion-tts)](https://github.com/aquarion-ai/aquarion-tts)

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
  - [Development Standards](#development-standards)
- [Installation](#installation)
  - [Details](#details)

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

`aquarion-tts` is distributed under the terms of the
[AGPL-3.0-only](https://spdx.org/licenses/AGPL-3.0-only.html) license.

### Development Standards

This project follows the following standard practices:

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) for
  commit messages.
- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) for versioning.
- [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

## Installation

1. Clone this repository.

1. Install [Devbox](https://www.jetify.com/docs/devbox/installing_devbox/)

1. Run:

   ```console
   devbox shell
   init
   pre-commit run --all-files
   check push
   check --help
   ```

### Details

- Devbox is a tool for creating per-project development environments using Nix.  It is
  used in this project for non-Python dev tools and bootstrapping.
- On first run, `devbox shell` will download and install all the needed system tools
  for the environment
- pre-commit is a tool for running certain checks and fixes on the code before commits
  and/or pushes.
- On the first run, `init` will download and install the base Python version, needed
  commands, hooks, etc.
- **NOTE:** No commit, push or pull request should or will be accepted unless all
  pre-commit and pre-push hooks pass.  No exceptions!
- Hatch is a tool for managing dependencies, builds, virtual environments and Python
  versions, as well as running tests, formatting, linting and typechecking.
- The `check` command calls Hatch to perform common tasks, while also making it easier
  to do so.
- `check push` runs all common tasks, like type checking, formatting, linting, unit
   tests, acceptance tests, coverage checks, etc.
- On first run, `check push` will download and install several files, etc.
