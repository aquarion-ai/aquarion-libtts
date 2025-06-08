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

"""Unit tests for _kokoro._plugin module."""

from typing import TYPE_CHECKING, Any, cast

import pytest

from aquarion.libs.libtts._kokoro._plugin import KokoroPlugin
from aquarion.libs.libtts._kokoro._settings import KokoroSettings
from aquarion.libs.libtts.api import (
    ITTSBackend,
    ITTSPlugin,
    ITTSSettings,
    JSONSerializableTypes,
)
from tests.api.ttssettings_test import AnotherTTSSettings
from tests.kokoro.conftest import INVALID_SETTINGS_CASES, SETTINGS_ARGS, SettingsDict

if TYPE_CHECKING:
    from collections.abc import Mapping


### KokoroPlugin Tests ###


## ITTSPlugin Protocol Conformity ##


def test_kokoroplugin_should_conform_to_its_protocol() -> None:
    plugin = KokoroPlugin()
    _: ITTSPlugin = plugin  # Typecheck protocol conformity
    assert isinstance(plugin, ITTSPlugin)  # Runtime check as well


def test_kokoroplugin_should_have_an_id_attribute() -> None:
    plugin = KokoroPlugin()
    assert hasattr(plugin, "id")


def test_kokoroplugin_id_should_be_immutable() -> None:
    plugin = KokoroPlugin()
    with pytest.raises(AttributeError, match="object has no setter"):
        plugin.id = "new_id"  # type:ignore[misc]


def test_kokoroplugin_id_should_have_the_correct_value() -> None:
    plugin = KokoroPlugin()
    assert plugin.id == "kokoro_v1"


## .get_display_name test


def test_kokoroplugin_get_display_name_should_accept_a_locale_argument() -> None:
    plugin = KokoroPlugin()
    plugin.get_display_name("en_CA")


def test_kokoroplugin_get_display_name_should_require_the_locale_argument() -> None:
    plugin = KokoroPlugin()
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        plugin.get_display_name()  # type:ignore[call-arg]


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("en_CA", "Kokoro"),
        ("en_US", "Kokoro"),
        ("en_GB", "Kokoro"),
        ("fr_CA", "Kokoro"),
        ("fr_FR", "Kokoro"),
    ],
)
def test_kokoroplugin_get_display_name_should_return_correct_display_name_for_locale(
    locale: str, expected: str
) -> None:
    plugin = KokoroPlugin()
    display_name = plugin.get_display_name(locale)
    assert display_name == expected


def test_kokoroplugin_get_display_name_should_return_a_fallback_if_locale_unknown() -> (
    None
):
    plugin = KokoroPlugin()
    display_name = plugin.get_display_name("ja")
    assert display_name == "Kokoro"


## .make_settings tests


@pytest.mark.parametrize(("attribute"), SETTINGS_ARGS)
def test_kokoroplugin_make_settings_should_use_default_values_when_no_values_given(
    attribute: str,
) -> None:
    plugin = KokoroPlugin()
    settings = plugin.make_settings()
    assert isinstance(settings, KokoroSettings)  # For the type checker
    assert (
        getattr(settings, attribute) == KokoroSettings.model_fields[attribute].default  # type:ignore[misc]
    )


@pytest.mark.parametrize(("attribute"), SETTINGS_ARGS)
def test_kokoroplugin_make_settings_should_use_given_values_when_values_are_given(
    real_settings_path_args: SettingsDict, attribute: str
) -> None:
    settings_dict = SETTINGS_ARGS.copy()
    settings_dict.update(real_settings_path_args)
    plugin = KokoroPlugin()
    settings = plugin.make_settings(
        from_dict=cast("Mapping[str, JSONSerializableTypes]", settings_dict)
    )
    assert isinstance(settings, KokoroSettings)  # For the type checker
    assert getattr(settings, attribute) == settings_dict.get(attribute)  # type:ignore[misc]


def test_kokoroplugin_make_settings_should_return_a_ittssettings_object() -> None:
    plugin = KokoroPlugin()
    settings = plugin.make_settings()
    _: ITTSSettings = settings  # Typecheck protocol conformity
    assert isinstance(settings, ITTSSettings)  # Runtime check as well


def test_kokoroplugin_make_settings_should_raise_an_error_if_an_invalid_key_given() -> (
    None
):
    plugin = KokoroPlugin()
    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        plugin.make_settings(from_dict={"invalid": None})


@pytest.mark.parametrize(("attr", "value", "err_msg"), INVALID_SETTINGS_CASES)  # type:ignore[misc]
def test_kokoroplugin_make_settings_should_raise_an_error_if_an_invalid_value_given(  # type:ignore[explicit-any,misc]
    attr: str,
    value: Any,  # noqa: ANN401
    err_msg: str,
) -> None:
    plugin = KokoroPlugin()
    with pytest.raises(ValueError, match=err_msg):
        plugin.make_settings(from_dict={attr: value})  # type:ignore[misc]


## .make_backend tests


def test_kokoroplugin_make_backend_should_require_a_settings_argument() -> None:
    plugin = KokoroPlugin()
    with pytest.raises(TypeError, match="missing *. required positional argument"):
        plugin.make_backend()  # type:ignore[call-arg]


def test_kokoroplugin_make_backend_should_use_the_given_settings() -> None:
    plugin = KokoroPlugin()
    expected_settings = plugin.make_settings()
    backend = plugin.make_backend(expected_settings)
    settings = backend.get_settings()
    assert isinstance(settings, KokoroSettings)  # For the type checker
    assert settings == expected_settings


def test_kokoroplugin_make_backend_should_return_a_ittsbackend_object() -> None:
    plugin = KokoroPlugin()
    settings = plugin.make_settings()
    backend = plugin.make_backend(settings)
    _: ITTSBackend = backend  # Typecheck protocol conformity
    assert isinstance(backend, ITTSBackend)  # Runtime check as well


def test_kokoroplugin_make_backend_should_raise_error_if_incorrect_settings_given() -> (
    None
):
    plugin = KokoroPlugin()
    settings = AnotherTTSSettings()
    with pytest.raises(TypeError, match="Incorrect settings type"):
        plugin.make_backend(settings)
