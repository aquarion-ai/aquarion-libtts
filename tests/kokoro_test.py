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

"""Unit tests for _kokoro module."""

import pytest

from aquarion.libs.libtts._kokoro import KokoroSettings, KokoroVoices
from aquarion.libs.libtts.api._ttssettings import ITTSSettings

### KokoroSettings Tests ###


@pytest.mark.parametrize(
    ("locale", "voice", "speed"),
    [
        ("en-US", KokoroVoices.af_heart, 1.0),
        ("en-GB", KokoroVoices.bf_emma, 0.5),
        ("fr-FR", KokoroVoices.ff_siwis, 0.75),
    ],
)
def test_kokorosettings_should_accept_attributes_as_kwargs(
    locale: str, voice: KokoroVoices, speed: float
) -> None:
    settings = KokoroSettings(locale=locale, voice=voice, speed=speed)
    assert settings.locale == locale
    assert settings.voice == voice
    assert settings.speed == speed


def test_kokorosettings_should_only_accept_keyword_arguments() -> None:
    with pytest.raises(
        TypeError, match="takes 1 positional argument but .* were given"
    ):
        KokoroSettings("en-GB")  # type: ignore [misc]


@pytest.mark.parametrize(
    ("attr", "value", "err_msg"),
    [
        ("locale", "xx-XX", "Invalid locale"),
        ("locale", "en-CA", "Unsupported locale"),
        ("voice", "xf_not_exist", "Input should be 'af_heart', "),
        ("voice", KokoroVoices.ff_siwis, "Invalid voice for the locale: en-US"),
        ("speed", -1, "greater than 0"),
        ("speed", 0, "greater than 0"),
        ("speed", 1.1, "less than or equal to 1"),
    ],
)
def test_kokorosettings_should_raise_an_exception_if_a_setting_is_invalid(
    attr: str, value: str | float, err_msg: str
) -> None:
    with pytest.raises(ValueError, match=err_msg):
        KokoroSettings(**{attr: value})  # type: ignore [arg-type]


@pytest.mark.parametrize(("attr"), ["locale", "voice", "speed", "lang_code"])
def test_kokorosettings_should_have_expected_attribute(
    attr: str,
) -> None:
    settings = KokoroSettings()
    assert hasattr(settings, attr)


def test_kokorosettings_should_not_allow_extra_arguments() -> None:
    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        KokoroSettings(extra_argument="value")  # type: ignore[call-arg]


def test_kokorosettings_should_not_allow_extra_attributes() -> None:
    settings = KokoroSettings()
    with pytest.raises(ValueError, match='object has no field "extra_attribute"'):
        settings.extra_attribute = "value"  # type: ignore[attr-defined]


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


def test_kokorosettings_to_dict_should_return_voices_as_strings() -> None:
    settings = KokoroSettings()
    settings_dict: dict[str, str | float] = settings.to_dict()
    assert isinstance(settings_dict["voice"], str)
    assert settings_dict["voice"] == "af_heart"  # Default voice as string


def test_kokorosettings_should_coerce_voice_strings_to_enum_on_instantiation() -> None:
    settings = KokoroSettings(voice="af_heart")  # type: ignore[arg-type]
    assert settings.voice == KokoroVoices.af_heart
    assert isinstance(settings.voice, KokoroVoices)


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
    settings = KokoroSettings(**{attr: value})  # type: ignore[arg-type]
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
