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

"""Unit tests for kokoro._hook module."""

import sys
from collections.abc import Generator
from contextlib import contextmanager
from typing import Final
from unittest.mock import patch

import pytest
from logot import Logot, logged

from aquarion.libs.libtts.api import tts_hookimpl
from aquarion.libs.libtts.kokoro._hook import register_tts_plugin
from aquarion.libs.libtts.kokoro._plugin import KokoroPlugin

KOKORO_DEPENDENCIES: Final = ["torch", "kokoro"]


@contextmanager
def disable_dependency(module: str) -> Generator[None, None, None]:
    backup = sys.modules[module]
    del sys.modules[module]
    with patch("sys.path", []):
        yield
    sys.modules[module] = backup


### register_tts_plugin() tests ###


def test_register_tts_plugin_should_return_a_kokoroplugin_instance() -> None:
    plugin = register_tts_plugin()
    assert isinstance(plugin, KokoroPlugin)


def test_register_tts_plugin_should_be_a_tts_hookimpl() -> None:
    assert hasattr(register_tts_plugin, f"{tts_hookimpl.project_name}_impl")


@pytest.mark.parametrize("module", KOKORO_DEPENDENCIES)
def test_register_tts_plugin_should_return_none_if_kokoro_is_not_installed(
    module: str,
) -> None:
    with disable_dependency(module):
        plugin = register_tts_plugin()
    assert plugin is None


def test_register_tts_plugin_should_log_registering(logot: Logot) -> None:
    register_tts_plugin()
    logot.assert_logged(logged.debug("Registering Kokoro TTS plugin."))


@pytest.mark.parametrize("module", KOKORO_DEPENDENCIES)
def test_register_tts_plugin_should_log_skipping(logot: Logot, module: str) -> None:
    with disable_dependency(module):
        register_tts_plugin()
    logot.assert_logged(
        logged.debug("Skipping Kokoro TTS plugin because of a missing dependency.")
    )
