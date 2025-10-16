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

"""Shared fixtures and code kokoro package tests."""

from __future__ import annotations

from typing import Final, TypedDict, cast

import pytest


class SettingsDict(TypedDict, total=False):
    """Types for KokoroSettings dicts and arguments."""

    locale: str
    voice: str
    speed: float
    device: str | None
    repo_id: str
    model_path: str | None
    config_path: str | None
    voice_path: str | None


SETTINGS_ARGS: Final[SettingsDict] = {
    "locale": "en_GB",
    "voice": "bf_emma",
    "speed": 0.8,
    "device": "cuda",
    "repo_id": "hexgrad/Kokoro-82M",
    "model_path": "kokoro-v1_0.pth",
    "config_path": "config.json",
    "voice_path": "af_heart.pt",
}


INVALID_SETTINGS_CASES: Final = [
    ("locale", "xx-XX", "Invalid locale"),
    ("locale", "es", "Unsupported locale"),
    ("locale", "hi", "Unsupported locale"),
    ("locale", "it", "Unsupported locale"),
    ("locale", "pt-br", "Unsupported locale"),
    ("locale", "ja", "Unsupported locale"),
    ("locale", "zh", "Unsupported locale"),
    ("voice", "xf_not_exist", "Input should be 'af_heart'"),
    ("voice", "ff_siwis", "Invalid voice for the locale: en_US"),
    ("speed", -1, "Input should be greater than or equal to 0.1"),
    ("speed", 0, "Input should be greater than or equal to 0.1"),
    ("speed", 2.1, "less than or equal to 2"),
    ("device", "bad_device", "Input should be 'cpu'"),
    ("model_path", "bad/exist", "Path does not point to a file"),
    ("config_path", "bad/exist", "Path does not point to a file"),
    ("voice_path", "bad/exist", "Path does not point to a file"),
]


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
        "en": "The identifier or path of the Kokoro TTS HuggingFace repository.",
        "fr": "L'identifiant ou le chemin du dépôt HuggingFace de Kokoro SSV.",
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
    for locale in ("en_US", "en_GB"):
        EXPECTED_SETTING_DESCRIPTIONS[setting_name][locale] = (
            EXPECTED_SETTING_DESCRIPTIONS[setting_name]["en"]
        )
for setting_name in EXPECTED_SETTING_DESCRIPTIONS:  # noqa: PLC0206
    for locale in ("fr_FR",):
        EXPECTED_SETTING_DESCRIPTIONS[setting_name][locale] = (
            EXPECTED_SETTING_DESCRIPTIONS[setting_name]["fr"]
        )


@pytest.fixture(scope="session")
def real_settings_path_args(
    tmp_path_factory: pytest.TempPathFactory,
) -> SettingsDict:
    tmp_dir_path = tmp_path_factory.mktemp("kokoro_data")
    path_args = {}
    for argument, file_name in SETTINGS_ARGS.items():
        if not argument.endswith("_path"):
            continue
        file_path = tmp_dir_path / cast("str", file_name)
        file_path.touch()
        path_args[argument] = str(file_path)
    return cast("SettingsDict", path_args)
