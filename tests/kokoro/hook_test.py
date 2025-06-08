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

"""Unit tests for _kokoro._hook module."""

import sys
from unittest.mock import patch

import pytest

from aquarion.libs.libtts._kokoro._hook import register_tts_plugin
from aquarion.libs.libtts._kokoro._plugin import KokoroPlugin
from aquarion.libs.libtts.api import tts_hookimpl


def test_register_tts_plugin_should_return_a_kokoroplugin_instance() -> None:
    plugin = register_tts_plugin()
    assert isinstance(plugin, KokoroPlugin)


def test_register_tts_plugin_should_be_a_tts_hookimpl() -> None:
    assert hasattr(register_tts_plugin, f"{tts_hookimpl.project_name}_impl")


@pytest.mark.parametrize("module", ["torch", "kokoro"])
def test_register_tts_plugin_should_return_none_if_kokoro_is_not_installed(
    module: str,
) -> None:
    backup = sys.modules[module]
    del sys.modules[module]
    # NOTE: We have to use unittest.mock.patch here because we need the context manager.
    #       We have to restore sys.path before the test ends in order to re-import the
    #       deleted module.
    with patch("sys.path", []):
        plugin = register_tts_plugin()
    sys.modules[module] = backup
    assert plugin is None
