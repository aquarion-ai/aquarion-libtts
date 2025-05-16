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

from aquarion.libs.libtts.api._plugins import (
    RegisterTTSBackendFuncType,
    load_tts_plugins,
    tts_hookimpl,
)
from aquarion.libs.libtts.api._ttsbackend import ITTSBackend, ITTSBackendFactory
from aquarion.libs.libtts.api._ttsregistry import (
    ITTSDisplayNameFactory,
    TTSRegistry,
    TTSRegistryRecord,
)
from aquarion.libs.libtts.api._ttssettings import (
    ITTSSettings,
    ITTSSettingsFactory,
    ITTSSettingsHolder,
    ITTSSettingsHolderFactory,
    JSONSerializableTypes,
)
from aquarion.libs.libtts.api._ttsspeechdata import TTSSpeechData

__all__ = [
    "ITTSBackend",
    "ITTSBackendFactory",
    "ITTSDisplayNameFactory",
    "ITTSSettings",
    "ITTSSettingsFactory",
    "ITTSSettingsHolder",
    "ITTSSettingsHolderFactory",
    "JSONSerializableTypes",
    "RegisterTTSBackendFuncType",
    "TTSRegistry",
    "TTSRegistryRecord",
    "TTSSpeechData",
    "load_tts_plugins",
    "tts_hookimpl",
]
