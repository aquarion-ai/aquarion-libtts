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

"""Unit tests for _kokoro._settings module."""

from pathlib import Path
from typing import Any, Final

import pytest

from aquarion.libs.libtts._kokoro._settings import (
    KokoroDeviceNames,
    KokoroSettings,
    KokoroVoices,
)
from aquarion.libs.libtts.api import ITTSSettings
from tests.kokoro.conftest import INVALID_SETTINGS_CASES, SETTINGS_ARGS, SettingsDict

SETTINGS_ATTRS: Final = [*list(SETTINGS_ARGS), "lang_code"]


### KokoroSettings Tests ###


def test_kokorosettings_should_accept_attributes_as_kwargs(
    real_settings_path_args: SettingsDict,
) -> None:
    arguments = SETTINGS_ARGS.copy()
    arguments.update(real_settings_path_args)
    KokoroSettings(**arguments)  # type:ignore[arg-type]


def test_kokorosettings_should_only_accept_keyword_arguments(
    real_settings_path_args: SettingsDict,
) -> None:
    arguments = SETTINGS_ARGS.copy()
    arguments.update(real_settings_path_args)
    with pytest.raises(
        TypeError, match="takes 1 positional argument but .* were given"
    ):
        KokoroSettings(*arguments.values())


@pytest.mark.parametrize("attribute", SETTINGS_ARGS)
def test_kokorosettings_should_store_given_settings_values(
    real_settings_path_args: SettingsDict, attribute: str
) -> None:
    arguments = SETTINGS_ARGS.copy()
    arguments.update(real_settings_path_args)
    settings = KokoroSettings(**arguments)  # type:ignore[arg-type]
    assert getattr(settings, attribute) == arguments.get(attribute)  # type:ignore[misc]


@pytest.mark.parametrize(("attr", "value", "err_msg"), INVALID_SETTINGS_CASES)  # type:ignore[misc]
def test_kokorosettings_should_raise_an_exception_if_a_setting_is_invalid(  # type:ignore[explicit-any,misc]
    attr: str,
    value: Any,  # noqa: ANN401
    err_msg: str,
) -> None:
    with pytest.raises(ValueError, match=err_msg):
        KokoroSettings(**{attr: value})  # type:ignore[misc]


@pytest.mark.parametrize(("attr"), SETTINGS_ATTRS)
def test_kokorosettings_should_have_expected_attributes(attr: str) -> None:
    settings = KokoroSettings()
    assert hasattr(settings, attr)


def test_kokorosettings_should_not_allow_extra_arguments() -> None:
    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        KokoroSettings(extra_argument="value")  # type:ignore[call-arg]


def test_kokorosettings_should_not_allow_extra_attributes() -> None:
    settings = KokoroSettings()
    with pytest.raises(ValueError, match='object has no field "extra_attribute"'):
        settings.extra_attribute = "value"  # type:ignore[attr-defined]


@pytest.mark.parametrize(
    ("locale", "voice", "expected"),
    [
        ("en-US", KokoroVoices.af_heart, "a"),
        ("en-GB", KokoroVoices.bf_emma, "b"),
        ("fr-FR", KokoroVoices.ff_siwis, "f"),
    ],
)
def test_kokorosettings_lang_code_should_return_the_correct_language_code(
    locale: str, voice: KokoroVoices, expected: str
) -> None:
    settings = KokoroSettings(locale=locale, voice=voice)
    assert settings.lang_code == expected


def test_kokorosettings_to_dict_should_return_voice_as_a_string() -> None:
    settings = KokoroSettings(voice=KokoroVoices.af_heart)
    settings_dict: dict[str, str | float] = settings.to_dict()
    assert isinstance(settings_dict["voice"], str)
    assert settings_dict["voice"] == "af_heart"


def test_kokorosettings_to_dict_should_return_device_as_a_string() -> None:
    settings = KokoroSettings(device=KokoroDeviceNames.cuda)
    settings_dict: dict[str, str | float] = settings.to_dict()
    assert isinstance(settings_dict["device"], str)
    assert settings_dict["device"] == "cuda"


def test_kokorosettings_should_coerce_voice_strings_to_enum_on_instantiation() -> None:
    settings = KokoroSettings(voice="af_heart")  # type:ignore[arg-type]
    assert settings.voice == KokoroVoices.af_heart
    assert isinstance(settings.voice, KokoroVoices)


def test_kokorosettings_should_coerce_device_strings_to_enum_on_instantiation() -> None:
    settings = KokoroSettings(device="cpu")  # type:ignore[arg-type]
    assert settings.device == KokoroDeviceNames.cpu
    assert isinstance(settings.device, KokoroDeviceNames)


@pytest.mark.parametrize(
    "attribute", [attr for attr in SETTINGS_ARGS if attr.endswith("_path")]
)
def test_kokorosettings_should_raise_an_error_if_file_path_does_not_exist(
    attribute: str,
) -> None:
    with pytest.raises(ValueError, match="Path does not point to a file"):
        KokoroSettings(**{attribute: Path("non-existant-path")})  # type:ignore[arg-type]


## ITTSSettings Protocol Conformity ##


def test_kokorosettings_should_conform_to_the_ittssettings_protocol() -> None:
    settings = KokoroSettings()
    _: ITTSSettings = settings  # Typecheck protocol conformity
    assert isinstance(settings, ITTSSettings)  # Runtime check as well


def test_kokorosettings_should_have_a_locale_attribute() -> None:
    settings: ITTSSettings = KokoroSettings()
    assert isinstance(settings.locale, str)


@pytest.mark.parametrize(
    ("attr", "value"),
    [("locale", "en-US"), ("voice", "af_heart"), ("speed", 1.0)],
)
def test_kokorosettings_to_dict_should_return_a_dict_of_all_settings_as_base_types(
    attr: str, value: str | float
) -> None:
    settings = KokoroSettings(**{attr: value})  # type:ignore[arg-type]
    settings_dict: dict[str, str | float] = settings.to_dict()
    assert settings_dict[attr] == value


def test_kokorosettings_should_equate_if_setting_values_are_equal() -> None:
    settings1 = KokoroSettings()
    settings2 = KokoroSettings()
    assert settings1 == settings2
    assert settings1 is not settings2


def test_kokorosettings_should_not_equate_if_setting_values_are_different() -> None:
    settings1 = KokoroSettings()
    settings2 = KokoroSettings(locale="en-GB", voice=KokoroVoices.bf_emma)
    assert settings1 != settings2
    assert settings1 is not settings2
