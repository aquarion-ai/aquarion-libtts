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

from collections.abc import Mapping
from typing import Final, cast

import pytest
from logot import Logot, logged

from aquarion.libs.libtts._kokoro._plugin import KokoroPlugin
from aquarion.libs.libtts._kokoro._settings import KokoroSettings
from aquarion.libs.libtts.api import (
    ITTSBackend,
    ITTSPlugin,
    ITTSSettings,
    JSONSerializableTypes,
    TTSSettingsSpecEntry,
)
from tests.unit.api.ttssettings_test import AnotherTTSSettings
from tests.unit.kokoro.conftest import (
    INVALID_SETTINGS_CASES,
    SETTINGS_ARGS,
    SettingsDict,
)

### KokoroPlugin Tests ###


def test_kokoroplugin_make_settings_should_log_settings_creation(logot: Logot) -> None:
    plugin = KokoroPlugin()
    settings = plugin.make_settings()
    logot.assert_logged(logged.debug(f"Created new KokoroSettings: {settings!s}"))


def test_kokoroplugin_make_backend_should_log_backend_creation(logot: Logot) -> None:
    plugin = KokoroPlugin()
    plugin.make_backend(plugin.make_settings())
    logot.assert_logged(logged.debug("Created new KokoroBackend."))


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
    with pytest.raises(TypeError, match=r"missing .* required positional argument"):
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
    expected_dict = SETTINGS_ARGS.copy()
    expected_dict.update(real_settings_path_args)
    plugin = KokoroPlugin()
    settings = plugin.make_settings(
        from_dict=cast("Mapping[str, JSONSerializableTypes]", expected_dict)
    )
    assert isinstance(settings, KokoroSettings)  # For the type checker
    settings_dict = cast("SettingsDict", settings.to_dict())
    assert settings_dict.get(attribute) == expected_dict.get(attribute)


def test_kokoroplugin_make_settings_should_return_a_ittssettings_object() -> None:
    plugin = KokoroPlugin()
    settings = plugin.make_settings()
    _: ITTSSettings = settings  # Typecheck protocol conformity
    assert isinstance(settings, ITTSSettings)  # Runtime check as well


def test_kokoroplugin_make_settings_should_raise_an_error_if_an_invalid_key_given(
    # Force line wrap in Ruff.
) -> None:
    plugin = KokoroPlugin()
    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        plugin.make_settings(from_dict={"invalid": None})


@pytest.mark.parametrize(("attr", "value", "err_msg"), INVALID_SETTINGS_CASES)
def test_kokoroplugin_make_settings_should_raise_an_error_if_an_invalid_value_given(
    attr: str,
    value: JSONSerializableTypes,
    err_msg: str,
) -> None:
    plugin = KokoroPlugin()
    with pytest.raises(ValueError, match=err_msg):
        plugin.make_settings(from_dict={attr: value})


## .make_backend tests


def test_kokoroplugin_make_backend_should_require_a_settings_argument() -> None:
    plugin = KokoroPlugin()
    with pytest.raises(TypeError, match=r"missing *. required positional argument"):
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


def test_kokoroplugin_make_backend_should_raise_error_if_incorrect_settings_given(
    # Force line wrap in Ruff.
) -> None:
    plugin = KokoroPlugin()
    settings = AnotherTTSSettings()
    with pytest.raises(TypeError, match="Incorrect settings type"):
        plugin.make_backend(settings)


## .get_settings_spec tests


def test_kokoroplugin_get_settings_spec_should_return_a_mapping_of_ttssettingsspecentry(
    # Force line wrap in Ruff.
) -> None:
    plugin = KokoroPlugin()
    spec = plugin.get_settings_spec()
    assert isinstance(spec, Mapping)
    assert all(isinstance(entry, TTSSettingsSpecEntry) for entry in spec.values())


def test_kokoroplugin_get_settings_spec_result_should_include_all_settings() -> None:
    plugin = KokoroPlugin()
    spec = plugin.get_settings_spec()
    assert sorted(spec.keys()) == sorted(SETTINGS_ARGS)


def test_kokoroplugin_get_settings_spec_result_should_be_immutable() -> None:
    plugin = KokoroPlugin()
    spec = plugin.get_settings_spec()
    with pytest.raises(TypeError, match="object does not support item assignment"):
        spec["new_key"] = "invalid"  # type:ignore[index]
    with pytest.raises(TypeError, match="object does not support item assignment"):
        spec["attr1"] = "also invalid"  # type:ignore[index]


## .get_setting_display_name tests


GET_SETTING_DISPLAY_NAME_ARGS: Final = {
    "setting_name": "locale",
    "locale": "en_CA",
}
EXPECTED_SETTING_DISPLAY_NAMES = {
    "locale": {
        "en": "Locale",
        "fr": "Paramètre de localisation",
    },
    "voice": {
        "en": "Voice",
        "fr": "Voix",
    },
    "speed": {
        "en": "Speed",
        "fr": "Vitesse",
    },
    "device": {
        "en": "Compute Device",
        "fr": "Périphérique de calcul",
    },
    "repo_id": {
        "en": "Repository ID",
        "fr": "Identifiant du dépôt",
    },
    "model_path": {
        "en": "Model File Path",
        "fr": "Chemin du fichier modèle",
    },
    "config_path": {
        "en": "Configuration File Path",
        "fr": "Chemin du fichier de configuration",
    },
    "voice_path": {
        "en": "Voice File Path",
        "fr": "Chemin du fichier vocal",
    },
}
for setting_name in EXPECTED_SETTING_DISPLAY_NAMES:  # noqa: PLC0206
    for locale in ("en_CA", "en_US", "en_GB"):
        EXPECTED_SETTING_DISPLAY_NAMES[setting_name][locale] = (
            EXPECTED_SETTING_DISPLAY_NAMES[setting_name]["en"]
        )
for setting_name in EXPECTED_SETTING_DISPLAY_NAMES:  # noqa: PLC0206
    for locale in ("fr_CA", "fr_FR"):
        EXPECTED_SETTING_DISPLAY_NAMES[setting_name][locale] = (
            EXPECTED_SETTING_DISPLAY_NAMES[setting_name]["fr"]
        )


def test_kokoroplugin_get_setting_display_name_should_accept_required_arguments(
    # Force line wrap in Ruff.
) -> None:
    plugin = KokoroPlugin()
    plugin.get_setting_display_name(**GET_SETTING_DISPLAY_NAME_ARGS)


@pytest.mark.parametrize("argument", GET_SETTING_DISPLAY_NAME_ARGS)
def test_kokoroplugin_get_setting_display_name_should_require_required_arguments(
    argument: str,
) -> None:
    args = GET_SETTING_DISPLAY_NAME_ARGS.copy()
    del args[argument]
    plugin = KokoroPlugin()
    with pytest.raises(TypeError, match="missing 1 required positional argument"):
        plugin.get_setting_display_name(**args)


@pytest.mark.parametrize(
    ("setting_name", "locale", "expected"),
    [
        (setting, locale, expected)
        for setting, info in EXPECTED_SETTING_DISPLAY_NAMES.items()
        for locale, expected in info.items()
    ],
)
def test_kokoroplugin_get_setting_display_name_should_return_correct_name_for_locale(
    setting_name: str, locale: str, expected: str
) -> None:
    plugin = KokoroPlugin()
    display_name = plugin.get_setting_display_name(setting_name, locale)
    assert display_name == expected


@pytest.mark.parametrize(
    ("setting_name", "expected"),
    [
        (setting, info["en_CA"])
        for setting, info in EXPECTED_SETTING_DISPLAY_NAMES.items()
    ],
)
def test_kokoroplugin_get_setting_display_name_should_return_fallback_if_locale_unknown(
    setting_name: str, expected: str
) -> None:
    plugin = KokoroPlugin()
    display_name = plugin.get_setting_display_name(setting_name, "ja")
    assert display_name == expected


## .get_setting_description tests


GET_SETTING_DESCRIPTION_ARGS: Final = {
    "setting_name": "locale",
    "locale": "en_CA",
}
EXPECTED_SETTING_DESCRIPTIONS = {
    "locale": {
        "en": "The regional or international locale setting.",
        "fr": "Le paramètre régional ou la norme locale internationale.",
    },
    "voice": {
        "en": "The voice used by the text-to-speech system.",
        "fr": "La voix utilisée par le système de synthèse vocale.",
    },
    "speed": {
        "en": "The speaking speed of the text-to-speech system.",
        "fr": "La vitesse de parole du système de synthèse vocale.",
    },
    "device": {
        "en": "The device used for running the TTS system (e.g., cpu or cuda).",
        "fr": (
            "Le périphérique utilisé pour exécuter le système de synthèse vocale"
            " (ex. : cpu ou cuda)."
        ),
    },
    "repo_id": {
        "en": "The identifier or path of the Kokoro TTS Git repository.",
        "fr": "L'identifiant ou le chemin du dépôt Git de Kokoro SSV.",
    },
    "model_path": {
        "en": (
            "The file path to the Kokoro TTS model file.  Required only for offline or "
            "air-gapped use; otherwise, files are downloaded and cached automatically."
        ),
        "fr": (
            "Le chemin du fichier modèle utilisé par Kokoro pour la synthèse vocale.  "
            "Nécessaire uniquement pour une utilisation hors ligne ou en environment "
            "isolé ; sinon, les fichiers sont téléchargés et "
            "mis en cache "
            "automatiquement."
        ),
    },
    "config_path": {
        "en": (
            "The file path to the Kokoro TTS configuration file.  Required only for "
            "offline or air-gapped use; otherwise, files are downloaded and cached "
            "automatically."
        ),
        "fr": (
            "Le chemin du fichier de configuration utilisé par Kokoro pour la synthèse "
            "vocale.  Nécessaire uniquement pour une utilisation hors ligne ou en "
            "environment isolé ; sinon, les fichiers sont téléchargés et "
            "mis en cache"
            " automatiquement."
        ),
    },
    "voice_path": {
        "en": (
            "The file path to the Kokoro TTS voice file.  Required only for offline or "
            "air-gapped use; otherwise, files are downloaded and cached automatically."
        ),
        "fr": (
            "Le chemin du fichier vocal utilisé par Kokoro pour la synthèse vocale.  "
            "Nécessaire uniquement pour une utilisation hors ligne ou en environment "
            "isolé ; sinon, les fichiers sont téléchargés et "
            "mis en cache "
            "automatiquement."
        ),
    },
}
for setting_name in EXPECTED_SETTING_DESCRIPTIONS:  # noqa: PLC0206
    for locale in ("en_CA", "en_US", "en_GB"):
        EXPECTED_SETTING_DESCRIPTIONS[setting_name][locale] = (
            EXPECTED_SETTING_DESCRIPTIONS[setting_name]["en"]
        )
for setting_name in EXPECTED_SETTING_DESCRIPTIONS:  # noqa: PLC0206
    for locale in ("fr_CA", "fr_FR"):
        EXPECTED_SETTING_DESCRIPTIONS[setting_name][locale] = (
            EXPECTED_SETTING_DESCRIPTIONS[setting_name]["fr"]
        )


def test_kokoroplugin_get_setting_description_should_accept_required_arguments(
    # Force line wrap in Ruff.
) -> None:
    plugin = KokoroPlugin()
    plugin.get_setting_description(**GET_SETTING_DESCRIPTION_ARGS)


@pytest.mark.parametrize("argument", GET_SETTING_DESCRIPTION_ARGS)
def test_kokoroplugin_get_setting_description_should_require_required_arguments(
    argument: str,
) -> None:
    args = GET_SETTING_DESCRIPTION_ARGS.copy()
    del args[argument]
    plugin = KokoroPlugin()
    with pytest.raises(TypeError, match=r"missing .* required positional argument"):
        plugin.get_setting_description(**args)


@pytest.mark.parametrize(
    ("setting_name", "locale"),
    [
        (setting, locale)
        for setting, info in EXPECTED_SETTING_DESCRIPTIONS.items()
        for locale in info
    ],
)
def test_kokoroplugin_get_setting_description_should_return_correct_value_for_locale(
    setting_name: str, locale: str
) -> None:
    expected = EXPECTED_SETTING_DESCRIPTIONS[setting_name][locale]
    plugin = KokoroPlugin()
    description = plugin.get_setting_description(setting_name, locale)
    assert description == expected


@pytest.mark.parametrize("setting_name", EXPECTED_SETTING_DESCRIPTIONS)
def test_kokoroplugin_get_setting_description_should_return_fallback_if_locale_unknown(
    setting_name: str,
) -> None:
    expected = EXPECTED_SETTING_DESCRIPTIONS[setting_name]["en_CA"]
    plugin = KokoroPlugin()
    description = plugin.get_setting_description(setting_name, "ja")
    assert description == expected
