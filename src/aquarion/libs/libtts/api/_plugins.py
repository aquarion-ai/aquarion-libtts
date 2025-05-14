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


"""Plugin system for aquarion-libtts plugins."""

import sys
from collections.abc import Callable

from pluggy import HookimplMarker, HookspecMarker, PluginManager

from aquarion.libs.libtts.api._ttsregistry import TTSRegistryRecord

type RegisterTTSBackendFuncType = Callable[[TTSRegistryRecord], None]

tts_hookspec = HookspecMarker("aquarion-libtts")
tts_hookimpl = HookimplMarker(tts_hookspec.project_name)


def load_tts_plugins(
    register_tts_backend_func: RegisterTTSBackendFuncType, *, validate: bool = False
) -> None:
    """Load all aquarion-tts plugins and call their hook(s).

    If validate is True, raises PluginValidationError if any plugin hook implementations
    do not conform to accepted hook specifications.
    """
    manager = PluginManager(tts_hookspec.project_name)
    manager.add_hookspecs(sys.modules[__name__])
    manager.load_setuptools_entrypoints(tts_hookimpl.project_name)
    if validate:
        manager.check_pending()
    manager.hook.register_tts_backend(register_func=register_tts_backend_func)


@tts_hookspec
def register_tts_backend(register_func: RegisterTTSBackendFuncType) -> None:
    """Plugin hook to register a TTS backend and it's settings.

    Implementation call registry_func with a TTSRegistryRecord instance contained all
    the required fields, including their ITTSBackendFactory and ITTSSettingsFactory
    implementations.
    """
