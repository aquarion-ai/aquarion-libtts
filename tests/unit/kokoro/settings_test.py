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

"""Unit tests for kokoro._settings module."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Final, cast

import pytest
from logot import Logot, logged

from aquarion.libs.libtts.api import (
    ITTSSettings,
    JSONSerializableTypes,
    TTSSettingsSpecEntry,
)
from aquarion.libs.libtts.kokoro.settings import (
    KokoroDeviceNames,
    KokoroLocales,
    KokoroSettings,
    KokoroVoices,
)
from tests.unit.kokoro.conftest import (
    INVALID_SETTINGS_CASES,
    SETTINGS_ARGS,
    SettingsDict,
)

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
        TypeError, match=r"takes 1 positional argument but .* were given"
    ):
        KokoroSettings(*arguments.values())


@pytest.mark.parametrize("attribute", SETTINGS_ARGS)
def test_kokorosettings_should_store_given_settings_values(
    real_settings_path_args: SettingsDict, attribute: str
) -> None:
    arguments = SETTINGS_ARGS.copy()
    arguments.update(real_settings_path_args)
    settings = KokoroSettings(**arguments)  # type:ignore[arg-type]
    settings_dict = cast("SettingsDict", settings.to_dict())
    assert settings_dict.get(attribute) == arguments.get(attribute)


@pytest.mark.parametrize(("attr", "value", "err_msg"), INVALID_SETTINGS_CASES)
def test_kokorosettings_should_raise_an_exception_if_a_setting_is_invalid(
    attr: str, value: JSONSerializableTypes, err_msg: str
) -> None:
    with pytest.raises(ValueError, match=err_msg):
        KokoroSettings(**{attr: value})  # type:ignore[arg-type]


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
    ("locale", "voice"),
    zip(
        KokoroLocales,
        [
            "af_heart",  # en_CA
            "af_heart",  # en_US
            "bf_emma",  # en_GB,
            "ff_siwis",  # fr_CA,
            "ff_siwis",  # fr_FR,
        ],
        strict=True,
    ),
)
def test_kokorosettings_should_accept_supported_locales(
    locale: str, voice: str
) -> None:
    settings = KokoroSettings(locale=locale, voice=voice)  # type:ignore[arg-type]
    assert str(settings.locale) == locale


@pytest.mark.parametrize(
    ("locale", "voice"),
    zip(
        [
            "en_CA",  # af_heart
            "en_US",  # af_bella
            "en_CA",  # af_nicole
            "en_US",  # am_fenrir
            "en_CA",  # am_michael
            "en_US",  # am_puck
            "en_GB",  # bf_emma
            "en_GB",  # bm_fable
            "en_GB",  # bm_george
            "fr_CA",  # ff_siwis
        ],
        KokoroVoices,
        strict=True,
    ),
)
def test_kokorosettings_should_accept_supported_voices(locale: str, voice: str) -> None:
    settings = KokoroSettings(locale=locale, voice=voice)  # type:ignore[arg-type]
    assert str(settings.locale) == locale


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
        KokoroSettings(**{attribute: Path("non-existent-path")})  # type:ignore[arg-type]


## .lang_code tests


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


## .to_dict tests


def test_kokorosettings_to_dict_should_return_voice_as_a_string() -> None:
    settings = KokoroSettings(voice=KokoroVoices.af_heart)
    settings_dict = cast("SettingsDict", settings.to_dict())
    assert isinstance(settings_dict["voice"], str)
    assert settings_dict["voice"] == "af_heart"


def test_kokorosettings_to_dict_should_return_device_as_a_string() -> None:
    settings = KokoroSettings(device=KokoroDeviceNames.cuda)
    settings_dict = cast("SettingsDict", settings.to_dict())
    assert isinstance(settings_dict["device"], str)
    assert settings_dict["device"] == "cuda"


def test_kokorosettings_to_dict_should_log_dictionary_creation(logot: Logot) -> None:
    settings = KokoroSettings(device=KokoroDeviceNames.cuda)
    settings_dict = cast("SettingsDict", settings.to_dict())
    logot.assert_logged(
        logged.debug(f"KokoroSettings dictionary created: {settings_dict!s}")
    )


## _make_spec tests


def test_kokorosettings_make_spec_should_return_a_mapping_of_ttssettingsspecentry(
    # Force line wrap in Ruff.
) -> None:
    spec = KokoroSettings._make_spec()  # noqa: SLF001
    assert isinstance(spec, Mapping)
    assert all(isinstance(entry, TTSSettingsSpecEntry) for entry in spec.values())


def test_kokorosettings_make_spec_result_should_include_all_settings() -> None:
    spec = KokoroSettings._make_spec()  # noqa: SLF001
    assert sorted(spec.keys()) == sorted(SETTINGS_ARGS)


def test_kokorosettings_make_spec_result_should_be_immutable() -> None:
    spec = KokoroSettings._make_spec()  # noqa: SLF001
    with pytest.raises(TypeError, match="object does not support item assignment"):
        spec["new_key"] = "invalid"  # type:ignore[index]
    with pytest.raises(TypeError, match="object does not support item assignment"):
        spec["attr1"] = "also invalid"  # type:ignore[index]


## _get_setting_display_name tests


def test_kokorosettings_get_setting_display_name_should_accept_a_setting_name() -> None:
    KokoroSettings._get_setting_display_name("locale")  # noqa: SLF001


def test_kokorosettings_get_setting_display_name_should_require_a_setting_name(
    # Force line wrap in Ruff.
) -> None:
    with pytest.raises(TypeError, match=r"missing .* required positional argument"):
        KokoroSettings._get_setting_display_name()  # type:ignore[call-arg]  # noqa: SLF001


@pytest.mark.parametrize(
    ("setting", "expected"),
    zip(
        SETTINGS_ARGS,
        [
            "Locale",  # locale
            "Voice",  # voice
            "Speed",  # speed
            "Compute Device",  # device
            "Repository ID",  # repo_id
            "Model File Path",  # model_path
            "Configuration File Path",  # config_path
            "Voice File Path",  # voice_path
        ],
        strict=True,
    ),
)
def test_kokorosettings_get_setting_display_name_should_return_the_display_name(
    setting: str, expected: str
) -> None:
    assert KokoroSettings._get_setting_display_name(setting) == expected  # noqa: SLF001


## _get_setting_description tests


SETTING_DESCRIPTIONS: Final = dict(
    zip(
        SETTINGS_ARGS,
        [
            "The regional or international locale setting.",  # locale
            "The voice used by the text-to-speech system.",  # voice
            "The speaking speed of the text-to-speech system.",  # speed
            "The device used for running the TTS system (e.g., cpu or cuda).",  # device
            (
                "The identifier or path of the Kokoro TTS HuggingFace repository."
            ),  # repo_id
            (
                "The file path to the Kokoro TTS model file.  Required only for offline"
                " or air-gapped use; otherwise, files are downloaded and cached "
                "automatically."
            ),  # model_path
            (
                "The file path to the Kokoro TTS configuration file.  Required only for"
                " offline or air-gapped use; otherwise, files are downloaded and cached"
                " automatically."
            ),  # config_path
            (
                "The file path to the Kokoro TTS voice file.  Required only for offline"
                " or air-gapped use; otherwise, files are downloaded and cached "
                "automatically."
            ),  # voice_path
        ],
        strict=True,
    )
)


def test_kokorosettings_get_setting_description_should_accept_a_setting_name() -> None:
    KokoroSettings._get_setting_description("locale")  # noqa: SLF001


def test_kokorosettings_get_setting_description_should_require_a_setting_name(
    # Force line wrap in Ruff.
) -> None:
    with pytest.raises(TypeError, match=r"missing .* required positional argument"):
        KokoroSettings._get_setting_description()  # type:ignore[call-arg]  # noqa: SLF001


@pytest.mark.parametrize(("setting"), SETTINGS_ARGS)
def test_kokorosettings_get_setting_description_should_return_the_description(
    setting: str,
) -> None:
    expected = SETTING_DESCRIPTIONS[setting]
    assert KokoroSettings._get_setting_description(setting) == expected  # noqa: SLF001


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
    [("locale", "en_US"), ("voice", "af_heart"), ("speed", 1.0)],
)
def test_kokorosettings_to_dict_should_return_a_dict_of_all_settings_as_base_types(
    attr: str, value: JSONSerializableTypes
) -> None:
    settings = KokoroSettings(**{attr: value})  # type:ignore[arg-type]
    settings_dict = cast("SettingsDict", settings.to_dict())
    assert settings_dict.get(attr) == value


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
