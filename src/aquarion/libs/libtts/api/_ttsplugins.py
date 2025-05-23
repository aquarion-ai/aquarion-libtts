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
from collections.abc import Mapping
from typing import Never, Protocol, runtime_checkable

from loguru import logger
from pluggy import HookimplMarker, HookspecMarker, PluginManager

from aquarion.libs.libtts.__about__ import __name__ as distribution_name
from aquarion.libs.libtts.api._ttsbackend import ITTSBackend
from aquarion.libs.libtts.api._ttssettings import (
    ITTSSettings,
    JSONSerializableTypes,
)

_tts_hookspec = HookspecMarker(distribution_name)
tts_hookimpl = HookimplMarker(_tts_hookspec.project_name)


@runtime_checkable
class ITTSPlugin(Protocol):
    """Common interface for all TTS Plugins."""

    @property
    def id(self) -> str:
        """Unique identifier for the plugin."""

    def get_display_name(self, locale: str) -> str:
        """Return a display name for the plugin appropriate for the given locale.

        The locale should be a POSIX-compliant locale string like `en_CA`, `zh-Hant`,
        `ca-ES-valencia`, or even `de_DE.UTF-8@euro`.  It can be a general as `fr` or as
        specific as `language_territory_script_variant@modifier`.

        Plugins are expected to to do their best to accommodate the given locale, but
        can fall back to more a general language variant.  E.g. from `en_CA` to `en`.

        If the given locale is not supported at all, then the plugin is expected to
        return a display name in it's default language.
        """

    def make_settings(
        self,
        from_dict: Mapping[str, JSONSerializableTypes] | None = None,
    ) -> ITTSSettings:
        """Return an object that conforms to the ITTSSettings protocol.

        If `from_dict` is not None, then the given values should be used to initialize
        the settings.

        If `from_dict` is None, then default values for all settings should be used.

        If any key or value in `from_dict` is invalid or missing for the concrete
        implementation of ITTSSettings that the factory will create, then a KeyError or
        ValueError should be raised.
        """

    def make_backend(self, settings: ITTSSettings) -> ITTSBackend:
        """Return an object that conforms to the ITTSBackend protocol.

        Custom or default settings must be provided to configure the TTS backend.

        Implementations of this interface should check that they are only getting the
        correct concrete settings class and raise TypeError if any other kind of
        concrete ITTSSettings is given.
        """


class TTSPluginRegistry:
    """Registry of all aquarion-libtts backend plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, ITTSPlugin] = {}
        self._enabled_plugins: set[str] = set()

    def load_plugins(self, *, validate: bool = False) -> None:
        """Load all aquarion-tts backend plugins.

        All plugins are disabled by default.  Use .enable() to enable a plugin.

        If validate is True, raises PluginValidationError if any plugin hook
        implementations do not conform to accepted hook specifications.
        """
        logger.debug(f"Loading TTS plugins for {_tts_hookspec.project_name}...")
        manager = PluginManager(_tts_hookspec.project_name)
        manager.add_hookspecs(sys.modules[__name__])
        manager.load_setuptools_entrypoints(tts_hookimpl.project_name)
        if validate:
            manager.check_pending()
        plugins: list[ITTSPlugin] = manager.hook.register_tts_plugin()
        if not plugins:
            message = (
                "No TTS plugins were found.  Please check your aquarion-libtts "
                "installation as this should not be possible."
            )
            raise RuntimeError(message)
        for plugin in plugins:
            logger.debug(f"Registered TTS plugin: {plugin.id}")
            self._plugins[plugin.id] = plugin
        logger.debug(f"Total TTS plugins registered: {len(self._plugins)}")

    def get_plugin(self, id_: str) -> ITTSPlugin:
        """Return the plugin the for the given id.

        Raises ValueError exception if the given id does not match any registered
        plugin.
        """
        try:
            return self._plugins[id_]
        except KeyError:
            self._raise_plugin_not_found(id_)

    def get_display_names(
        self, locale: str, *, include_disabled: bool = False
    ) -> dict[str, str]:
        """Return the ids and display names of all the registered TTS plugins."""
        return {
            plugin.id: plugin.get_display_name(locale)
            for plugin in self._plugins.values()
            if (plugin.id in self._enabled_plugins) or include_disabled
        }

    def enable(self, id_: str) -> None:
        """Enable a TTS plugin for inclusion in .get_display_names().

        Raises ValueError exception if the given id does not match any registered
        plugin.
        """
        if id_ not in self._plugins:
            self._raise_plugin_not_found(id_)
        self._enabled_plugins.add(id_)
        logger.debug(f"Enabled TTS plugin: {id_}")

    def disable(self, id_: str) -> None:
        """Disable a TTS plugin from inclusion in .get_display_names().

        Raises ValueError exception if the given id does not match any registered
        plugins.
        """
        if id_ not in self._plugins:
            self._raise_plugin_not_found(id_)
        self._enabled_plugins.discard(id_)
        logger.debug(f"Disabled TTS plugin: {id_}")

    ## Internal methods

    def _raise_plugin_not_found(self, id_: str) -> Never:
        """Shared method for when a backend is not registered."""
        message = f"TTS plugin not found: {id_}"
        raise ValueError(message)

    def _register_test_plugin(self, plugin: ITTSPlugin) -> None:
        """Support for unit testing this class."""
        self._plugins[plugin.id] = plugin


@_tts_hookspec
def register_tts_plugin() -> ITTSPlugin:  # type: ignore [empty-body]
    """Plugin hook to register a TTS backend plugin.

    Implementations must return an instance of ITTSPlugin.
    """
