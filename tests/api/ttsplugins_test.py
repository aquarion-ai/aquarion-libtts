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

"""Unit tests for the .api._plugins module."""

import importlib
from typing import Never

import pytest
from pluggy import PluginValidationError

from aquarion.libs.libtts.api import RegisterTTSBackendFuncType, tts_hookimpl
from aquarion.libs.libtts.api._ttsplugins import load_tts_plugins, register_tts_backend
from aquarion.libs.libtts.api._ttsregistry import TTSRegistry, TTSRegistryRecord
from tests.api.ttsregistry_test import REGISTRY_RECORD_REQUIRED_ARGUMENTS

### .load_tts_plugins tests

# Based on: https://github.com/pytest-dev/pluggy/blob/main/testing/test_pluginmanager.py


class DummyNamespace:
    """Dummy namespace (fake module) for our dummy hook implementation."""

    @tts_hookimpl
    def register_tts_backend(self, register_func: RegisterTTSBackendFuncType) -> None:
        record = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
        register_func(record)

    @tts_hookimpl
    def invalid_hook(self) -> Never:
        message = "This should never run"  # pragma: no cover
        raise NotImplementedError(message)  # pragma: no cover


class DummyEntryPoint:
    """Dummy entry point for plugin loading."""

    name = "dummy"
    group = tts_hookimpl.project_name
    value = "dummy:dummy"

    def load(self) -> DummyNamespace:
        return DummyNamespace()


class Distribution:
    """Dummy distribution containing out dummy entry point."""

    entry_points = (DummyEntryPoint(),)


def dummy_distributions() -> tuple[Distribution, ...]:
    return (Distribution(),)


def test_load_plugins_should_accept_a_register_backend_function_argument() -> None:
    registry = TTSRegistry()
    load_tts_plugins(registry.register)


def test_load_plugins_should_require_the_register_backend_function_argument() -> None:
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        load_tts_plugins()  # type: ignore [call-arg]


def test_load_plugins_should_accept_an_optional_validate_argument() -> None:
    registry = TTSRegistry()
    load_tts_plugins(registry.register, validate=False)


def test_load_plugins_should_require_validate_to_be_a_keyword_only_argument() -> None:
    registry = TTSRegistry()
    with pytest.raises(
        TypeError, match="takes .* positional argument.? but .* were given"
    ):
        load_tts_plugins(registry.register, False)  # type: ignore [misc]  # noqa: FBT003


def test_load_plugins_should_load_plugins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(importlib.metadata, "distributions", dummy_distributions)
    registry = TTSRegistry()
    load_tts_plugins(registry.register)
    assert registry.get_record("I am a key")


def test_load_plugins_should_raise_error_if_validate_true_and_invalid_hookimpl(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(importlib.metadata, "distributions", dummy_distributions)
    registry = TTSRegistry()
    with pytest.raises(PluginValidationError, match="unknown hook .* in plugin"):
        load_tts_plugins(registry.register, validate=True)


### .register_tts_backend spec tests


def test_register_backend_should_be_a_hookspec() -> None:
    assert hasattr(register_tts_backend, "aquarion-libtts_spec")


def test_register_backend_should_accept_a_register_function() -> None:
    registry = TTSRegistry()
    register_tts_backend(registry.register)


def test_register_backend_should_require_the_register_function() -> None:
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        register_tts_backend()  # type: ignore [call-arg]
