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


"""Unit tests for the ITTSSettings protocol.

These tests serve mostly to document the expectations of all ITTSSettings
implementations.
"""

from collections.abc import Mapping
from typing import Any, cast

import pytest

from aquarion.libs.libtts.api._ttssettings import (
    ITTSSettings,
    ITTSSettingsFactory,
    ITTSSettingsHolder,
    ITTSSettingsHolderFactory,
    JSONSerializableTypes,
)

### ITTSSettings Tests ###


class DummyTTSSettings:
    """Dummy ITTSSettings to test the protocol.

    Specific implementations here do not matter, the only important thing is to conform
    to the ITTSSettings protocol.
    """

    def __init__(self, attr1: str = "default") -> None:
        self.attr1 = attr1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DummyTTSSettings):
            # Since extension beyond the base protocol is not restricted, we are not
            # testing the negative case.  Especially since this is just part of the
            # normal __eq__() pattern.  Hence the no cover.
            return NotImplemented  # pragma: no cover
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


def test_ittssettings_should_conform_to_its_protocol() -> None:
    settings = DummyTTSSettings()
    _: ITTSSettings = settings  # Typecheck protocol conformity
    assert isinstance(settings, ITTSSettings)  # Runtime check as well


def test_ittssettings_to_dict_should_return_a_dict_of_all_settings_as_base_types() -> (
    None
):
    settings = DummyTTSSettings()
    settings_dict: dict[str, str] = settings.to_dict()
    assert settings_dict["attr1"] == "default"


def test_ittssettings_validate_should_do_nothing_if_all_settings_are_valid() -> None:
    settings = DummyTTSSettings()
    settings.validate()


def test_ittssettings_validate_should_raise_an_exception_if_a_setting_is_invalid() -> (
    None
):
    settings = DummyTTSSettings()
    settings.attr1 = 666  # type: ignore [assignment]
    with pytest.raises(TypeError):
        settings.validate()


def test_ittssettings_is_valid_should_return_true_if_all_settings_are_valid() -> None:
    settings = DummyTTSSettings()
    assert settings.is_valid()


def test_ittssettings_is_valid_should_return_false_if_any_settings_are_invalid() -> (
    None
):
    settings = DummyTTSSettings()
    settings.attr1 = 666  # type: ignore [assignment]
    assert not settings.is_valid()


def test_ittssettings_should_equate_if_setting_values_are_equal() -> None:
    settings1 = DummyTTSSettings()
    settings2 = DummyTTSSettings()
    assert settings1 == settings2
    assert settings1 is not settings2


def test_ittssettings_should_not_equate_if_setting_values_are_different() -> None:
    settings1 = DummyTTSSettings()
    settings2 = DummyTTSSettings(attr1="not default")
    assert settings1 != settings2
    assert settings1 is not settings2


### ITTSSettingsFactory Tests ###


def dummy_make_ittssettings(
    from_dict: Mapping[str, JSONSerializableTypes] | None = None,
) -> DummyTTSSettings:
    """Return a DummyTTSSettings.

    Dummy factory function to test the ITTSSettingsFactory protocol.

    Specific implementations here do not matter, the only important thing is to conform
    to the ITTSSettings protocol.
    """
    if from_dict is None:
        settings = DummyTTSSettings()
    else:
        settings = DummyTTSSettings(attr1=cast("str", from_dict["attr1"]))
    return settings


def test_ittssettingsfactory_should_conform_to_its_protocol() -> None:
    _: ITTSSettingsFactory[DummyTTSSettings] = (
        dummy_make_ittssettings  # Typecheck protocol conformity
    )
    assert isinstance(
        dummy_make_ittssettings, ITTSSettingsFactory
    )  # Runtime check as well


def test_ittssettingsfactory_should_use_default_values_when_no_values_are_given() -> (
    None
):
    settings = dummy_make_ittssettings()
    assert settings.attr1 == "default"


def test_ittssettingsfactory_should_use_given_values_when_values_are_given() -> None:
    settings = dummy_make_ittssettings(from_dict={"attr1": "custom"})
    assert settings.attr1 == "custom"


def test_ittssettingsfactory_should_return_a_ittssettings_object() -> None:
    settings = dummy_make_ittssettings()
    _: ITTSSettings = settings  # Typecheck protocol conformity
    assert isinstance(settings, ITTSSettings)  # Runtime check as well


### ITTSSettingsHolder Tests ###


class DummyTTSSettingsHolder:
    """Dummy TTS Settings Holder to test the protocol.

    Specific implementations here do not matter, the only important thing is to conform
    to the TTSSettingsHolder protocol.
    """

    @property
    def settings(self) -> DummyTTSSettings:
        return self._settings

    @settings.setter
    def settings(self, new_settings: DummyTTSSettings) -> None:
        self._settings = new_settings

    def __init__(self) -> None:
        self.settings = DummyTTSSettings()


def test_ittssettingsholder_should_conform_to_its_protocol() -> None:
    holder = DummyTTSSettingsHolder()
    _: ITTSSettingsHolder[DummyTTSSettings] = holder  # Typecheck protocol conformity
    assert isinstance(holder, ITTSSettingsHolder)  # Runtime check as well


def test_ittssettingsholder_should_have_a_settings_attribute() -> None:
    holder = DummyTTSSettingsHolder()
    assert hasattr(holder, "settings")


def test_ittssettingsholder_settings_should_be_settable() -> None:
    holder = DummyTTSSettingsHolder()
    new_settings = DummyTTSSettings(attr1="custom")
    holder.settings = new_settings
    assert holder.settings == new_settings


### ITTSSettingsHolderFactory Tests ###


def dummy_make_ittssettingsholder(settings: DummyTTSSettings) -> DummyTTSSettingsHolder:
    holder = DummyTTSSettingsHolder()
    holder.settings = settings
    return holder


def test_ittssettingsholderfactory_should_conform_to_its_protocol() -> None:
    _: ITTSSettingsHolderFactory[DummyTTSSettings] = (
        dummy_make_ittssettingsholder  # Typecheck protocol conformity
    )
    assert isinstance(
        dummy_make_ittssettingsholder, ITTSSettingsHolderFactory
    )  # Runtime check as well


def test_ittssettingsholderfactory_should_require_a_settings_argument() -> None:
    with pytest.raises(TypeError, match="missing *. required positional argument"):
        dummy_make_ittssettingsholder()  # type: ignore [call-arg]


def test_ittssettingsholderfactory_should_use_given_settings() -> None:
    settings = DummyTTSSettings("custom")
    holder = dummy_make_ittssettingsholder(settings)
    assert holder.settings.attr1 == "custom"


def test_ittssettingsholderfactory_should_return_a_ittssettingsholder_object() -> None:
    settings = DummyTTSSettings()
    holder = dummy_make_ittssettingsholder(settings)
    _: ITTSSettingsHolder[DummyTTSSettings] = holder  # Typecheck protocol conformity
    assert isinstance(holder, ITTSSettingsHolder)  # Runtime check as well
