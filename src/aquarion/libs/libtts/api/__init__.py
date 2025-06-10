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


"""Public interfaces for aquarion-libtts."""

from aquarion.libs.libtts.api._i18n import load_language
from aquarion.libs.libtts.api._ttsbackend import ITTSBackend, TTSAudioSpec
from aquarion.libs.libtts.api._ttsplugins import (
    ITTSPlugin,
    TTSPluginRegistry,
    tts_hookimpl,
)
from aquarion.libs.libtts.api._ttssettings import (
    ITTSSettings,
    ITTSSettingsHolder,
    JSONSerializableTypes,
)

__all__ = [
    "ITTSBackend",
    "ITTSPlugin",
    "ITTSSettings",
    "ITTSSettingsHolder",
    "JSONSerializableTypes",
    "TTSAudioSpec",
    "TTSPluginRegistry",
    "load_language",
    "tts_hookimpl",
]
