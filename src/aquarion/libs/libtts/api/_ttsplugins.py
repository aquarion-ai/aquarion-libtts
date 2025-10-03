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

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any, Never, Protocol, runtime_checkable

from loguru import logger
from pluggy import HookimplMarker, HookspecMarker, PluginManager

from aquarion.libs.libtts.__about__ import __name__ as distribution_name

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from aquarion.libs.libtts.api._ttsbackend import ITTSBackend
    from aquarion.libs.libtts.api._ttssettings import (
        ITTSSettings,
        JSONSerializableTypes,
        TTSSettingsSpecEntry,
        TTSSettingsSpecEntryTypes,
    )

_tts_hookspec = HookspecMarker(distribution_name)


if os.getenv("SPHINX_BUILD") != "1":
    tts_hookimpl = HookimplMarker(_tts_hookspec.project_name)
else:
    # NOTE: This is here to work around the fact the Sphinx's autosummary extension does
    #       not support documenting module-level variables. :(  At least not in v8.2.3.
    def tts_hookimpl(**kwargs: Any) -> Callable[[], ITTSPlugin | None]:  # type: ignore  # noqa: ANN401, PGH003
        """Decorate a function to mark it as a TTS plugin registration hook.

        This is a decorator.

        The decorated function is expected to return an ITTSPlugin or None if no plugin
        is to be registered.  E.g. Missing dependencies, incompatible hardware, etc.

        For more detailed usage options, see the
        `Pluggy package <https://pluggy.readthedocs.io/en/stable/#implementations>`__.

        """


@runtime_checkable
class ITTSPlugin(Protocol):
    """Common interface for all TTS Plugins."""

    @property
    def id(self) -> str:
        """Unique identifier for the plugin.

        The id must be unique across all Aquarion libtts plugins.
        """

    def get_display_name(self, locale: str) -> str:
        """Return a display name for the plugin appropriate for the given locale.

        The locale should be a POSIX-compliant locale string like `en_CA`, `zh-Hant`,
        `ca-ES-valencia`, or even `de_DE.UTF-8@euro`.  It can be as general as `fr` or
        as specific as `language_territory_script_variant@modifier`.

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

        This function is expected to validate it's inputs.  If any setting is invalid
        for the concrete implementation of ITTSSettings that the factory will create,
        then a KeyError, ValueError or TypeError (or subclass thereof) should be raised.
        """

    def make_backend(self, settings: ITTSSettings) -> ITTSBackend:
        """Return an object that conforms to the ITTSBackend protocol.

        Custom or default settings must be provided to configure the TTS backend.

        Implementations of this interface should check that they are only getting the
        correct concrete settings class and raise TypeError if any other kind of
        concrete ITTSSettings is given.
        """

    def get_settings_spec(
        self,
    ) -> Mapping[str, TTSSettingsSpecEntry[TTSSettingsSpecEntryTypes]]:
        """Return a specification that describes all the backend's settings.

        Returns an immutable mapping of from setting key/attribute to
        TTSSettingsSpecEntry instances.

        Implementations should probably return a MappingProxyType to achieve the
        immutability.
        """

    def get_setting_display_name(self, setting_name: str, locale: str) -> str:
        """Return the given setting's display name appropriate for the given locale.

        The locale should be a POSIX-compliant or standard format locale string like
        `en_CA`, `zh-Hant`, `ca-ES-valencia`, or even `de_DE.UTF-8@euro`.  It can be as
        general as `fr` or as specific as `language_territory_script_variant@modifier`.

        Plugins are expected to to do their best to accommodate the given locale, but
        can fall back to more a general language variant.  E.g. from `en_CA` to `en`.

        If the given locale is not supported at all, then the plugin is expected to
        return a display name in it's default language.
        """

    def get_setting_description(self, setting_name: str, locale: str) -> str:
        """Return the given setting's description appropriate for the given locale.

        The locale should be a POSIX-compliant or standard format locale string like
        `en_CA`, `zh-Hant`, `ca-ES-valencia`, or even `de_DE.UTF-8@euro`.  It can be as
        general as `fr` or as specific as `language_territory_script_variant@modifier`.

        Plugins are expected to to do their best to accommodate the given locale, but
        can fall back to more a general language variant.  E.g. from `en_CA` to `en`.

        If the given locale is not supported at all, then the plugin is expected to
        return a description in it's default language.
        """


class TTSPluginRegistry:
    """Registry of all aquarion-libtts backend plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, ITTSPlugin] = {}
        self._enabled_plugins: set[str] = set()

    def load_plugins(self, *, validate: bool = True) -> None:
        """Load all aquarion-tts backend plugins.

        All plugins are disabled by default.  Use .enable() to enable a plugin.

        If validate is True (the default), raises PluginValidationError if any plugin
        hook implementations do not conform to accepted hook specifications.
        """
        logger.debug(f"Loading TTS plugins for {_tts_hookspec.project_name}...")
        manager = PluginManager(_tts_hookspec.project_name)
        manager.add_hookspecs(sys.modules[__name__])
        manager.load_setuptools_entrypoints(tts_hookimpl.project_name)
        if validate:
            manager.check_pending()
        # Hooks that return None are filtered out automatically by Pluggy.
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

    def list_plugin_ids(
        self, *, only_disabled: bool = False, list_all: bool = False
    ) -> set[str]:
        """Return the list of plugin IDs.

        By default, only enabled plugins are listed.
        If disabled_only_is True, then only the disabled plugins are listed.
        If all True, then all plugins are listed regardless of their enabled/disabled
        status.
        If both arguments are True, then a ValueError is raised.
        """
        if only_disabled and list_all:
            message = (
                "Invalid argument combination. disabled_only and all cannot both be "
                "True."
            )
            raise ValueError(message)
        if only_disabled:
            return {id_ for id_ in self._plugins if not self.is_enabled(id_)}
        if list_all:
            return set(self._plugins)
        return {id_ for id_ in self._plugins if self.is_enabled(id_)}

    def get_plugin(self, id_: str) -> ITTSPlugin:
        """Return the plugin the for the given id.

        Raises ValueError exception if the given id does not match any registered
        plugin.
        """
        try:
            return self._plugins[id_]
        except KeyError:
            self._raise_plugin_not_found(id_)

    def is_enabled(self, plugin_id: str) -> bool:
        """Return True if the plugin of the given ID is enabled, False otherwise."""
        return plugin_id in self._enabled_plugins

    def enable(self, plugin_id: str) -> None:
        """Enable a TTS plugin for inclusion in .get_display_names().

        Raises ValueError exception if the given id does not match any registered
        plugin.
        """
        if plugin_id not in self._plugins:
            self._raise_plugin_not_found(plugin_id)
        self._enabled_plugins.add(plugin_id)
        logger.debug(f"Enabled TTS plugin: {plugin_id}")

    def disable(self, plugin_id: str) -> None:
        """Disable a TTS plugin from inclusion in .get_display_names().

        Raises ValueError exception if the given id does not match any registered
        plugins.
        """
        if plugin_id not in self._plugins:
            self._raise_plugin_not_found(plugin_id)
        self._enabled_plugins.discard(plugin_id)
        logger.debug(f"Disabled TTS plugin: {plugin_id}")

    ## Internal methods

    def _raise_plugin_not_found(self, plugin_id: str) -> Never:
        """Shared method for when a backend is not registered."""
        message = f"TTS plugin not found: {plugin_id}"
        raise ValueError(message)

    def _register_test_plugin(self, plugin: ITTSPlugin) -> None:
        """Support for unit testing this class."""
        self._plugins[plugin.id] = plugin


@_tts_hookspec
def register_tts_plugin() -> ITTSPlugin | None:
    """Plugin hook to register a TTS backend plugin.

    Implementations must return an instance of ITTSPlugin.

    Returning None skips plugin registration.  This can be useful if required conditions
    are not met at runtime.  (E.g. Missing extras or dependencies, etc.)
    """
