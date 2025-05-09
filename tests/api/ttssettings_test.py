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


"""Unit tests for the TTSSettings protocol.

These tests serve mostly to document the expectations of all TTSSettings
implementations.
"""

from typing import Any

import pytest

from aquarion.libs.libtts.api.ttssettings import TTSSettings


class DummyTTSSettings:
    """Dummy TTSSettings to test the protocol.

    Specific implementations here do not matter, the only important thing is to conform
    to the TTSSettings protocol.
    """

    def __init__(self, attr1: str = "default") -> None:
        self.attr1 = attr1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DummyTTSSettings):
            raise NotImplementedError
        return self.attr1 == other.attr1

    def to_dict(self) -> dict[str, Any]:  # type: ignore [explicit-any]
        return {"attr1": self.attr1}  # type: ignore [misc]

    def validate(self) -> None:
        if not isinstance(self.attr1, str):
            raise TypeError

    def is_valid(self) -> bool:
        try:
            self.validate()
        except TypeError:
            return False
        return True


def assert_typecheck_conforms_to_protocol(settings: TTSSettings) -> TTSSettings:
    """Enable the type checker validate conformance with the TTSSettings protocol."""
    assert isinstance(settings, TTSSettings)
    return settings


def test_ttssettings_should_conform_to_ttssettings_protocol() -> None:
    settings = DummyTTSSettings()
    assert_typecheck_conforms_to_protocol(settings)


def test_ttssettings_to_dict_should_return_a_dict_of_all_settings_as_base_types() -> (
    None
):
    settings = DummyTTSSettings()
    settings_dict: dict[str, str] = settings.to_dict()
    assert settings_dict["attr1"] == "default"


def test_ttssettings_validate_should_do_nothing_if_all_settings_are_valid() -> None:
    settings = DummyTTSSettings()
    settings.validate()


def test_ttssettings_validate_should_raise_an_exception_if_any_setting_is_invalid() -> (
    None
):
    settings = DummyTTSSettings()
    settings.attr1 = 666  # type: ignore [assignment]
    with pytest.raises(TypeError):
        settings.validate()


def test_ttssettings_is_valid_should_return_true_if_all_settings_are_valid() -> None:
    settings = DummyTTSSettings()
    assert settings.is_valid()


def test_ttssettings_is_valid_should_return_false_if_any_settings_are_invalid() -> None:
    settings = DummyTTSSettings()
    settings.attr1 = 666  # type: ignore [assignment]
    assert not settings.is_valid()


def test_ttssettings_should_equate_if_setting_values_are_equal() -> None:
    settings1 = DummyTTSSettings()
    settings2 = DummyTTSSettings()
    assert settings1 == settings2
    assert settings1 is not settings2


def test_ttssettings_should_not_equate_if_setting_values_are_different() -> None:
    settings1 = DummyTTSSettings()
    settings2 = DummyTTSSettings(attr1="not default")
    assert settings1 != settings2
    assert settings1 is not settings2
