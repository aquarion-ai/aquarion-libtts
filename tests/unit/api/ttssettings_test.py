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


"""Unit tests for api._ttssettings.

These tests serve mostly to document the expectations of all ITTSSettings
implementations.
"""

from dataclasses import FrozenInstanceError
from typing import Final, TypedDict

import pytest

from aquarion.libs.libtts.api import (
    ITTSSettings,
    ITTSSettingsHolder,
    JSONSerializableTypes,
)
from aquarion.libs.libtts.api._ttssettings import (
    TTSSettingsSpecEntry,
    TTSSettingsSpecEntryTypes,
)

### ITTSSettings Tests ###


class DummyTTSSettings:  # noqa: PLW1641
    """Dummy ITTSSettings to test the protocol.

    Specific implementations here do not matter, the only important thing is to conform
    to the ITTSSettings protocol.
    """

    def __init__(self, attr1: str | None = None) -> None:
        if attr1 is None:
            attr1 = "default"
        self.attr1 = attr1
        self.locale = "en-CA"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DummyTTSSettings):
            # Since extension beyond the base protocol is not restricted, we are not
            # testing the negative case.  Especially since this is just part of the
            # normal __eq__() pattern.  Hence the no cover.
            return NotImplemented  # pragma: no cover
        return self.attr1 == other.attr1

    def to_dict(self) -> dict[str, JSONSerializableTypes]:
        return {"attr1": self.attr1}


class AnotherTTSSettings:  # noqa: PLW1641
    """NOT the DummyTTSSettings class."""

    # These need to exist to conform to the ITTSSetting protocol, but are not actually
    # used or needed for the tests.

    locale = "fr-CA"

    def __eq__(self, other: object) -> bool:
        return False  # pragma: no cover

    def to_dict(self) -> dict[str, JSONSerializableTypes]:
        return {}  # pragma: no cover


def test_ittssettings_should_conform_to_its_protocol() -> None:
    settings = DummyTTSSettings()
    _: ITTSSettings = settings  # Typecheck protocol conformity
    assert isinstance(settings, ITTSSettings)  # Runtime check as well


def test_ittssettings_should_have_a_locale_attribute() -> None:
    settings: ITTSSettings = DummyTTSSettings()
    assert isinstance(settings.locale, str)


def test_ittssettings_to_dict_should_return_a_dict_of_all_settings_as_base_types() -> (
    None
):
    settings = DummyTTSSettings()
    settings_dict: dict[str, JSONSerializableTypes] = settings.to_dict()
    assert settings_dict["attr1"] == "default"


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


### ITTSSettingsHolder Tests ###


class DummyTTSSettingsHolder:
    """Dummy TTS Settings Holder to test the protocol.

    Specific implementations here do not matter, the only important thing is to conform
    to the ITTSSettingsHolder protocol.
    """

    def __init__(self) -> None:
        self._settings = DummyTTSSettings()

    def get_settings(self) -> DummyTTSSettings:
        return self._settings

    def update_settings(self, new_settings: ITTSSettings) -> None:
        if not isinstance(new_settings, DummyTTSSettings):
            message = f"Incorrect settings type: [{type(new_settings)}]."
            raise TypeError(message)
        self._settings = new_settings


def test_ittssettingsholder_should_conform_to_its_protocol() -> None:
    holder = DummyTTSSettingsHolder()
    _: ITTSSettingsHolder = holder  # Typecheck protocol conformity
    assert isinstance(holder, ITTSSettingsHolder)  # Runtime check as well


def test_ittssettingsholder_get_settings_should_return_an_ittssettings() -> None:
    holder = DummyTTSSettingsHolder()
    settings = holder.get_settings()
    _: ITTSSettings = settings  # Typecheck protocol conformity
    assert isinstance(settings, ITTSSettings)  # Runtime check as well


def test_ittssettingsholder_update_settings_should_accept_a_settings_argument() -> None:
    holder = DummyTTSSettingsHolder()
    holder.update_settings(DummyTTSSettings())


def test_ittssettingsholder_update_settings_should_require_the_settings_argument() -> (
    None
):
    holder = DummyTTSSettingsHolder()
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        holder.update_settings()  # type:ignore[call-arg]


def test_ittssettingsholder_update_settings_should_not_return_anything() -> None:
    # CQS principle: Commands should not return anything.
    holder = DummyTTSSettingsHolder()
    result: None = holder.update_settings(DummyTTSSettings())  # type:ignore[func-returns-value]
    assert result is None


def test_ittssettingsholder_update_settings_should_update_the_settings() -> None:
    holder = DummyTTSSettingsHolder()
    orig_settings = holder.get_settings()
    new_settings = DummyTTSSettings(attr1="new settings")
    holder.update_settings(new_settings)
    updated_settings = holder.get_settings()
    assert updated_settings == new_settings
    assert updated_settings != orig_settings


def test_ittssettingsholder_update_settings_should_raise_error_if_incorrect_type() -> (
    None
):
    holder = DummyTTSSettingsHolder()
    incorrect_settings = AnotherTTSSettings()
    with pytest.raises(TypeError, match="Incorrect settings type"):
        holder.update_settings(incorrect_settings)


### TTSSettingsSpecEntry tests ###


class SpecEntryArgsType[T: TTSSettingsSpecEntryTypes](TypedDict):
    """TypedDict for augments to pass to TTSSettingsSpecEntry."""

    type: type[T]
    min: int | None
    max: int | None
    values: frozenset[T] | None


SPEC_ENTRY_ARGS: Final[SpecEntryArgsType[int]] = {
    "type": int,
    "min": 5,
    "max": 10,
    "values": frozenset([5, 7, 9]),
}


def test_ttssettingsspecentry_should_accept_expected_arguments() -> None:
    TTSSettingsSpecEntry[int](**SPEC_ENTRY_ARGS)


def test_ttssettingsspecentry_should_require_the_type_argument() -> None:
    args = SPEC_ENTRY_ARGS.copy()
    del args["type"]  # type:ignore[misc]
    with pytest.raises(TypeError, match="missing .* required keyword-only argument"):
        TTSSettingsSpecEntry[int](**args)


def test_ttssettingsspecentry_should_accept_only_keyword_arguments() -> None:
    with pytest.raises(
        TypeError, match="takes 1 positional argument but .* were given"
    ):
        TTSSettingsSpecEntry(*SPEC_ENTRY_ARGS.values())  # type:ignore[call-arg]


@pytest.mark.parametrize("attribute", SPEC_ENTRY_ARGS.keys())
def test_ttssettingsspecentry_should_be_immutable(attribute: str) -> None:
    entry = TTSSettingsSpecEntry[int](**SPEC_ENTRY_ARGS)
    with pytest.raises(FrozenInstanceError, match="cannot assign to field"):
        setattr(entry, attribute, SPEC_ENTRY_ARGS[attribute])  # type:ignore[literal-required,misc]
