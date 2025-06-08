# SPDX-FileCopyrightText: 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
# SPDX-License-Identifier: AGPL-3.0-only

# Part of the aquarion-libtts library of the Aquarion AI project.
# Copyright (C) 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

"""Shared fixtures and code _kokoro package tests."""

from pathlib import Path
from typing import Final, TypedDict, cast

import pytest

from aquarion.libs.libtts._kokoro._settings import KokoroVoices


class SettingsDict(TypedDict, total=False):
    """Types for KokoroSettings dicts and arguments."""

    locale: str
    voice: KokoroVoices
    speed: float
    device: str | None
    repo_id: str
    model_path: Path | None
    config_path: Path | None
    voice_path: Path


SETTINGS_ARGS: Final[SettingsDict] = {
    "locale": "en-GB",
    "voice": KokoroVoices.bf_emma,
    "speed": 0.8,
    "device": "cuda",
    "repo_id": "hexgrad/Kokoro-82M",
    "model_path": Path("kokoro-v1_0.pth"),
    "config_path": Path("config.json"),
    "voice_path": Path("af_heart.pt"),
}


INVALID_SETTINGS_CASES: Final = [
    ("locale", "xx-XX", "Invalid locale"),
    ("locale", "en-CA", "Unsupported locale"),
    ("voice", "xf_not_exist", "Input should be 'af_heart'"),
    ("voice", KokoroVoices.ff_siwis, "Invalid voice for the locale: en-US"),
    ("speed", -1, "greater than 0"),
    ("speed", 0, "greater than 0"),
    ("speed", 1.1, "less than or equal to 1"),
    ("device", "bad_device", "Input should be 'cpu'"),
    ("model_path", Path("bad/exist"), "Path does not point to a file"),
    ("config_path", Path("bad/exist"), "Path does not point to a file"),
    ("voice_path", Path("bad/exist"), "Path does not point to a file"),
]


@pytest.fixture(scope="session")
def real_settings_path_args(
    tmp_path_factory: pytest.TempPathFactory,
) -> SettingsDict:
    tmp_dir_path = tmp_path_factory.mktemp("kokoro_data")
    path_args = {}
    for argument, file_name in SETTINGS_ARGS.items():
        if not argument.endswith("_path"):
            continue
        file_path = tmp_dir_path / cast("str", file_name)
        file_path.touch()
        path_args[argument] = file_path
    return cast("SettingsDict", path_args)
