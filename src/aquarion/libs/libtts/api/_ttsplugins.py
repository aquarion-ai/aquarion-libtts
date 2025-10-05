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

    def tts_hookimpl(**kwargs: Any) -> Callable[[], ITTSPlugin | None]:  # type: ignore  # noqa: ANN401, PGH003  # pragma: no cover
        """Decorate a function to mark it as a TTS plugin registration hook.

        This is a decorator.

        The decorated function is expected to return an :class:`ITTSPlugin` or
        :obj:`None` if no plugin is to be registered.  E.g. Missing dependencies,
        incompatible hardware, etc.

        For more detailed usage options, see the
        `Pluggy package <https://pluggy.readthedocs.io/en/stable/#implementations>`__.

        """


@runtime_checkable
class ITTSPlugin(Protocol):
    """Common interface for all TTS Plugins."""

    @property
    def id(self) -> str:
        """A unique identifier for the plugin.

        The id must be unique across all Aquarion libtts plugins.  Also, it is
        recommended to include at least a major version number as a suffix so that
        multiple versions / implementations of a plugin can be installed and supported
        simultaneously.  E.g. for backwards compatibility.

        This should be read-only.

        Example:
            kokoro_v1

        """

    def get_display_name(self, locale: str) -> str:
        """Return the display name for the plugin, appropriate for the given locale.

        A display name is one that is human-friendly as opposed to any kind of unique
        key that code would care about.

        Args:
            locale:
                The locale should be a POSIX-compliant (i.e. using underscores) or
                CLDR-compliant (i.e. using hyphens) locale string like ``en_CA``,
                ``zh-Hant``, ``ca-ES-valencia``, or even ``de_DE.UTF-8@euro``.  It can
                be as general as ``fr`` or as specific as
                ``language_territory_script_variant@modifier``.

                Plugins are expected to to do their best to accommodate the given
                locale, but can fall back to more a general language variant.  E.g. from
                ``en_CA`` to ``en``.

        Returns:
            The display name of the plugin in a language appropriate for the given
            locale.  If the given locale is not supported at all, then the plugin is
            expected to return a display name in it's default language, or English if
            that is preferred.

        """

    def make_settings(
        self,
        from_dict: Mapping[str, JSONSerializableTypes] | None = None,
    ) -> ITTSSettings:
        """Create and return an appropriate settings object for the TTS backend.

        This is a factory method.

        Args:
            from_dict:
                If it is not None, then the given values should be used to initialize
                the settings.

                If it is None, then default values for all settings should be used.

        Returns:
            An instance of a compatible :class:`ITTSSettings` implementation with all
            settings values valid for immediate use.

        Raises:
            KeyError, ValueError or TypeError: This function is expected to validate
                it's inputs.  If any setting is invalid for the concrete implementation
                of :class:`ITTSSettings` that the factory will create, then an exception
                should be raised.

        """

    def make_backend(self, settings: ITTSSettings) -> ITTSBackend:
        """Create and return a TTS backend instance.

        This is a factory method.

        Args:
            settings: Custom or default settings must be provided to configure the TTS
                backend.

        Returns:
            A configured and ready to use TTS backend.

        Raises:
            TypeError: Implementations of this interface must check that they are
                getting their own :class:`ITTSSettings` implementation and should raise
                an exception if any other plugin's :class:`ITTSSettings` is given
                instead.

        """

    def get_settings_spec(
        self,
    ) -> Mapping[str, TTSSettingsSpecEntry[TTSSettingsSpecEntryTypes]]:
        """Return a specification that describes all the backend's settings.

        Returns:
            An immutable mapping of from setting attribute name to
            :class:`TTSSettingsSpecEntry` instances.

            Implementations should probably return a :class:`MappingProxyType` to
            achieve the immutability.

        """

    def get_setting_display_name(self, setting_name: str, locale: str) -> str:
        """Return the given setting's display name, appropriate for the given locale.

        A display name is one that is human-friendly as opposed to any kind of unique
        key that code would care about.

        Args:
            setting_name: The name of the setting as returned from
                :meth:`get_settings_spec` mapping keys.
            locale:
                The locale should be a POSIX-compliant (i.e. using underscores) or
                CLDR-compliant (i.e. using hyphens) locale string like ``en_CA``,
                ``zh-Hant``, ``ca-ES-valencia``, or even ``de_DE.UTF-8@euro``.  It can
                be as general as ``fr`` or as specific as
                ``language_territory_script_variant@modifier``.

                Plugins are expected to to do their best to accommodate the given
                locale, but can fall back to more a general language variant.  E.g. from
                ``en_CA`` to ``en``.

        Returns:
            The display name of the setting in a language appropriate for the given
            locale.  If the given locale is not supported at all, then the plugin is
            expected to return a display name in it's default language, or English if
            that is preferred.

        Raises:
            KeyError or AttributeError: If the given setting name is not a recognized
                setting.

        """

    def get_setting_description(self, setting_name: str, locale: str) -> str:
        """Return the given setting's description, appropriate for the given locale.

        Args:
            setting_name: The name of the setting as returned from
                :meth:`get_settings_spec` mapping keys.
            locale:
                The locale should be a POSIX-compliant (i.e. using underscores) or
                CLDR-compliant (i.e. using hyphens) locale string like ``en_CA``,
                ``zh-Hant``, ``ca-ES-valencia``, or even ``de_DE.UTF-8@euro``.  It can
                be as general as ``fr`` or as specific as
                ``language_territory_script_variant@modifier``.

                Plugins are expected to to do their best to accommodate the given
                locale, but can fall back to more a general language variant.  E.g. from
                ``en_CA`` to ``en``.

        Returns:
            The display name of the setting in a language appropriate for the given
            locale.  If the given locale is not supported at all, then the plugin is
            expected to return a display name in it's default language, or English if
            that is preferred.

        Raises:
            KeyError or AttributeError: If the given setting name is not a recognized
                setting.

        """


class TTSPluginRegistry:
    """Registry of all aquarion-libtts backend plugins.

    TTS backends and everything related to them are created / accessed through
    :class:`ITTSPlugin` instances.  The plugin registry is responsible for finding,
    loading, listing, enabling, disabling and giving access to those plugins.

    """

    def __init__(self) -> None:
        self._plugins: dict[str, ITTSPlugin] = {}
        self._enabled_plugins: set[str] = set()

    def load_plugins(self, *, validate: bool = True) -> None:
        """Load all aquarion-libtts backend plugins.

        Plugins are discovered by searching for
        `pyproject.toml entry points <https://packaging.python.org/en/latest/specifications/pyproject-toml/#entry-points>`__
        named `aquarion-libtts`, then searching those entry points for hook functions
        decorated with :deco:`tts_hookimpl`, and finally calling those hook functions.
        The plugins returned by those hook functions are then stored in the plugin
        registry and made accessible.

        Note:
            All plugins are disabled by default.  Use :meth:`enable` to enable a plugin.

        Args:
            validate: If :obj:`True` (the default), then an exception is raised if any
                hook functions do not conform to expected hook specification.

        Raises:
            PluginValidationError: If ``validate`` is True and a hook function does not
                conform to the expected specification.

        Examples:
            .. code:: toml

                [project.entry-points.'aquarion-libtts']
                my_plugin_v1 = "package.hook"

            .. code:: python

                @tts_hookimpl
                def register_my_tts_plugin() -> ITTSPlugin | None:
                    from package.plugin import MyTTSPlugin
                    return MyTTSPlugin()

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
        """Return the set of plugin IDs.

        By default, only enabled plugins are listed.

        Args:
            only_disabled: If this is :obj:`True`, then only the *disabled* plugins are
                listed.
            list_all: If this is :obj:`True`, then *all* plugins are listed, regardless
                of their enabled/disabled status.

        Raises:
            ValueError: If both arguments are :obj:`True`.

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

    def get_plugin(self, id_: str) -> ITTSPlugin:  # noqa: D417
        """Return the plugin the for the given ID.

        Args:
            `id_`: The ID of the desired already loaded plugin.  E.g. ``kokoro_v1``.

        Raises:
            ValueError: If the given ID does not match any registered plugin.

        """
        try:
            return self._plugins[id_]
        except KeyError:
            self._raise_plugin_not_found(id_)

    def is_enabled(self, plugin_id: str) -> bool:
        """Return :obj:`True` if the plugin is enabled, :obj:`False` otherwise.

        Args:
            plugin_id: The ID of the plugin in question.

        Returns:
            :obj:`True` if the plugin is enabled, :obj:`False` otherwise.

        """
        return plugin_id in self._enabled_plugins

    def enable(self, plugin_id: str) -> None:
        """Enable a TTS plugin for inclusion in :meth:`list_plugin_ids`.

        The idea behind enabled vs disabled plugins is that it allows one to manage
        which plugins are listed / displayed to a user, independently of all the plugins
        that are installed / loaded.  I.e. It allows for filtering which plugins one
        wants exposed and which should be kept hidden.  E.g. Some plugins could be not
        supported by your application, even thought they got installed with some other
        dependency.

        Args:
            plugin_id: The ID of the desired plugin.

        Raises:
            ValueError: If the given ID does not match any registered plugin.

        """
        if plugin_id not in self._plugins:
            self._raise_plugin_not_found(plugin_id)
        self._enabled_plugins.add(plugin_id)
        logger.debug(f"Enabled TTS plugin: {plugin_id}")

    def disable(self, plugin_id: str) -> None:
        """Disable a TTS plugin for inclusion in :meth:`list_plugin_ids`.

        Args:
            plugin_id: The ID of the desired plugin.

        Raises:
            ValueError: If the given ID does not match any registered plugin.

        Note:
            Disabling a plugin does not affect any existing instances of that plugin in
            any way.  So, proper TTS backend instance management and stopping must still
            be handled separately.

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
