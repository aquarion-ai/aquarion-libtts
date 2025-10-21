<!--
    SPDX-FileCopyrightText: 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
    SPDX-License-Identifier: CC-BY-SA-4.0
-->

<!--
    aquarion-libtts documentation © 2025-present by Krys Lawrence is licensed under
    Creative Commons Attribution-ShareAlike 4.0 International. To view a copy of this
    license, visit <https://creativecommons.org/licenses/by-sa/4.0/>
-->

# Aquarion AI - Text To Speech (TTS) Library

Experiment in creating a scalable local AI voice chat bot.

[![Static Badge](https://img.shields.io/badge/Part_of-Aquarion_AI-blue)](https://github.com/aquarion-ai)
[![Docs Licence](https://img.shields.io/badge/docs_licence-CC_BY_SA_4.0-red)](https://creativecommons.org/licenses/by-sa/4.0/)
[![REUSE status](https://api.reuse.software/badge/github.com/aquarion-ai/aquarion-libtts)](https://api.reuse.software/info/github.com/aquarion-ai/aquarion-libtts)
<!-- markdownlint-disable MD013 -->
<!--
[![PyPI - License](https://img.shields.io/pypi/l/aquarion-libtts)](https://pypi.org/project/aquarion-libtts)
-->
<!-- markdownlint-enable MD013 -->

<!-- markdownlint-disable MD013 -->
<!--
[![PyPI - Version](https://img.shields.io/pypi/v/aquarion-libtts.svg)](https://pypi.org/project/aquarion-libtts)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aquarion-libtts.svg)](https://pypi.org/project/aquarion-libtts)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/aquarion-libtts)](https://pypi.org/project/aquarion-libtts)
[![PyPI - Types](https://img.shields.io/pypi/types/aquarion-libtts)](https://pypi.org/project/aquarion-libtts)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/aquarion-libtts)](https://pypi.org/project/aquarion-libtts)
[![PyPI - Format](https://img.shields.io/pypi/format/aquarion-libtts)](https://pypi.org/project/aquarion-libtts)
[![PyPI - Status](https://img.shields.io/pypi/status/aquarion-libtts)](https://pypi.org/project/aquarion-libtts)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/aquarion-libtts)](https://pypi.org/project/aquarion-libtts)
-->
<!-- markdownlint-enable MD013 -->

[![build](https://github.com/aquarion-ai/aquarion-libtts/actions/workflows/build.yml/badge.svg)](https://github.com/aquarion-ai/aquarion-libtts/actions/workflows/build.yml)
[![Test Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/justkrys/079b402971d82c07d05c74f37c57b088/raw/aquarion-ai_aquarion-libtts__main__test.json)](https://github.com/aquarion-ai/aquarion-libtts/actions)
[![Acceptance Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/justkrys/079b402971d82c07d05c74f37c57b088/raw/aquarion-ai_aquarion-libtts__main__accept.json)](https://github.com/aquarion-ai/aquarion-libtts/actions)
[![Total Vulnerabilities](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/justkrys/079b402971d82c07d05c74f37c57b088/raw/aquarion-ai_aquarion-libtts__main__sec_total.json)](https://github.com/aquarion-ai/aquarion-libtts/actions)
[![Highest Vulnerability Severity](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/justkrys/079b402971d82c07d05c74f37c57b088/raw/aquarion-ai_aquarion-libtts__main__sec_highest.json)](https://github.com/aquarion-ai/aquarion-libtts/actions)
[![Docs build](https://app.readthedocs.org/projects/aquarion-libtts/badge/?version=latest)](https://aquarion-libtts.readthedocs.io/en/latest/)

[![GitHub Open Issues](https://img.shields.io/github/issues/aquarion-ai/aquarion-libtts)](https://github.com/aquarion-ai/aquarion-libtts/issues)
[![GitHub Closed Issues](https://img.shields.io/github/issues-closed/aquarion-ai/aquarion-libtts)](https://github.com/aquarion-ai/aquarion-libtts/issues)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/aquarion-ai/aquarion-libtts)](https://github.com/aquarion-ai/aquarion-libtts/activity)
[![GitHub last commit](https://img.shields.io/github/last-commit/aquarion-ai/aquarion-libtts)](https://github.com/aquarion-ai/aquarion-libtts/activity)
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

<!-- include_start_1 -->

## Description

### About Aquarion AI

The overall goal of the Aquarion AI project is to create an LLM-based voice chat bot /
assistant, but to build it in such a way that is can be scaled down to a single desktop
app, and all the way up to a distributed multi-server, horizontally scalable system.
Also, desired is a taking head / avatar who's mouth moves with the speech.  Lastly, it
should all run locally / offline, even in an air gapped environment.  Oh, and it should
be modular enough to support multiple alternate STT, LLM and TTS models/engines/options.

For high-level documentation on the overall Aquarion AI project, see the
[aquarion-docs](https://github.com/aquarion-ai/aquarion-docs) project.

### About aquarion-libtts

This project contains the library of Text To Speech (TTS) backend components for
Aquarion AI.

For documentation for this specific project, see
[aquarion-libtts documentation](https://aquarion-libtts.readthedocs.io/en/latest/).

<!-- include_end_1 -->

## Installation

See the
[Getting Started](https://aquarion-libtts.readthedocs.io/en/latest/getting_started.html)
section of the documentation.

## Usage

See the
[Getting Started](https://aquarion-libtts.readthedocs.io/en/latest/getting_started.html)
section of the documentation.

## Support

### Disclaimer

While this project is FOSS and you are welcome to use it, know that I am making this for
myself. So do not expect any kind of support or updates or maintenance or longevity.
*Caveat Emptor*.

## Roadmap

- Integrate in to the larger Aquarion AI project.
- Add more TTS backends.

## Contributing

If, despite the disclaimer above, you still want to try to contribute, then see the
[Contributing](https://aquarion-libtts.readthedocs.io/en/latest/contributing.html)
section of the documentation.

<!-- include_start_2 -->

## Authors and Acknowledgements

Aquarion AI and aquarion-libtts was created by Krys Lawrence.

## Copyright and Licence

- `aquarion-libtts` is © 2025-present by Krys Lawrence.

- `aquarion-libtts` code is licensed under the terms of the
  [AGPL-3.0-only](https://www.gnu.org/licenses/agpl-3.0.en.html#license-text) licence.

- `aquarion-libtts` documentation is licensed under the terms of the
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) licence.

<!-- include_end_2 -->

## Project Status

This project is in the Alpha stage of development.  Early days, lots of bugs and
anything change.
