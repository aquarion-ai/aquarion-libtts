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


"""Plugin system for *aquarion-libtts* plugins."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Never, Protocol, runtime_checkable

from loguru import logger
from pluggy import HookimplMarker, HookspecMarker, PluginManager

from aquarion.libs.libtts.__about__ import __name__ as distribution_name

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from collections.abc import Set as AbstractSet

    from aquarion.libs.libtts.api._ttsbackend import ITTSBackend
    from aquarion.libs.libtts.api._ttssettings import (
        ITTSSettings,
        JSONSerializableTypes,
        TTSSettingsSpecType,
    )

_tts_hookspec = HookspecMarker(distribution_name)
tts_hookimpl = HookimplMarker(_tts_hookspec.project_name)

# NOTE: This is here only to provide a better presentation in the API docs.
#       mkdocstrings-python parses the AST instead of importing the module, so it finds
#       this definition even if it is not actually defined at import time.
if False:

    def tts_hookimpl(**kwargs: Any) -> Callable[[], ITTSPlugin | None]:  # type: ignore  # noqa: ANN401, PGH003  # pragma: no cover
        """Decorate a function to mark it as a TTS plugin registration hook.

        This is a decorator.

        The decorated function is expected to accept no arguments and to return an
        [ITTSPlugin][aquarion.libs.libtts.api.ITTSPlugin], or [None][] if no plugin is
        to be registered.  E.g. Missing dependencies, incompatible hardware, etc.

        For more detailed usage options, see the
        [Pluggy](https://pluggy.readthedocs.io/en/stable/#implementations) package.

        Args:
            kwargs: Any keyword arguments supported by
                [Pluggy](https://pluggy.readthedocs.io/en/stable/#implementations).

        Returns:
            The decorated function, but marked as a TTS plugin registration hook.

        Example:
            ```python linenums="1"
            @tts_hookimpl
            def register_my_tts_plugin() -> ITTSPlugin | None:
                # NOTE: It is important that we do not import our plugin class or
                #       related packages at module import time.
                #       This hook needs to be able to run even when our required
                #       dependencies, etc. are not installed.
                try:
                    import dependency
                except ModuleNotFoundError:
                    return None
                from package.plugin import MyTTSPlugin

                return MyTTSPlugin()
            ```

        """


@runtime_checkable
class ITTSPlugin(Protocol):
    """Common interface for all TTS Plugins."""

    @property
    def id(self) -> str:
        """A unique identifier for the plugin.

        The ID must be unique across all *aquarion-libtts* plugins.  Also, it is
        recommended to include at least a major version number as a suffix so that
        multiple versions / implementations of a plugin can be installed and supported
        simultaneously.  E.g. for backwards compatibility.

        Returns:
            The unique identifier for the plugin.

        Example:
            `kokoro_v1`

        Note:
            This should be a read-only property.

        """

    def get_display_name(self, locale: str) -> str:
        """Return the display name for the plugin, appropriate for the given locale.

        A display name is one that is human-friendly as opposed to any kind of unique
        key that code would care about.

        Args:
            locale:
                The locale should be a POSIX-compliant (i.e. using underscores) or
                CLDR-compliant (i.e. using hyphens) locale string like `en_CA`,
                `zh-Hant`, `ca-ES-valencia`, or even `de_DE.UTF-8@euro`.  It can be as
                general as `fr` or as specific as
                `language_territory_script_variant@modifier`.

                Plugins are expected to to do their best to accommodate the given
                locale, but can fall back to a more general language variant if that is
                all it supports.  E.g. from `en_CA` to just `en`.

        Returns:
            The display name of the plugin in a language appropriate for the given
                locale.  If the given locale is not supported at all, then the plugin is
                expected to return a display name in it's default language, or English
                if that is preferred.

        """

    def make_settings(
        self,
        from_dict: Mapping[str, JSONSerializableTypes] | None = None,
    ) -> ITTSSettings:
        """Create and return an appropriate settings object for the TTS backend.

        This is a factory method.

        Args:
            from_dict:
                If it is not [None][], then the given values should be used to
                initialize the settings.

                If it is [None][], then default values for all settings should be used.

        Note:
            If `from_dict` is provided, then each setting value in it is expected to be
            validated by this method.

        Returns:
            A compatible settings instance with all settings values valid for immediate
                use.

        Raises:
            KeyError, ValueError or TypeError: If any setting value is invalid for the
                concrete implementation of
                [ITTSSettings][aquarion.libs.libtts.api.ITTSSettings] that this
                factory will create, then an exception should be raised.

        """

    def make_backend(self, settings: ITTSSettings) -> ITTSBackend:
        """Create and return a TTS backend instance.

        This is a factory method.

        Args:
            settings: Custom or default settings must be provided to configure the TTS
                backend.  See
                [make_settings][aquarion.libs.libtts.api.ITTSPlugin.make_settings] for
                details.

        Returns:
            A configured TTS backend, ready to use.

        Raises:
            TypeError: Implementations of this interface must check that they are
                getting their own [ITTSSettings][aquarion.libs.libtts.api.ITTSSettings]
                implementation and should raise an exception if any other plugin's
                settings object is given instead.

        """

    def get_settings_spec(
        self,
    ) -> TTSSettingsSpecType:
        """Return a specification that describes all the backend's settings.

        Returns:
            An immutable mapping of from setting attribute name to
                [TTSSettingsSpecEntry][aquarion.libs.libtts.api.TTSSettingsSpecEntry]
                instances.

                Implementations should probably return a [types.MappingProxyType][] to
                achieve the immutability.

        """

    def get_setting_display_name(self, setting_name: str, locale: str) -> str:
        """Return the given setting's display name, appropriate for the given locale.

        A display name is one that is human-friendly as opposed to any kind of unique
        key that code would care about.

        Args:
            setting_name: The name of the setting as returned from
                [get_settings_spec][aquarion.libs.libtts.api.ITTSPlugin.get_settings_spec]
                mapping keys.
            locale:
                The locale should be a POSIX-compliant (i.e. using underscores) or
                CLDR-compliant (i.e. using hyphens) locale string like `en_CA`,
                `zh-Hant`, `ca-ES-valencia`, or even `de_DE.UTF-8@euro`.  It can be as
                general as `fr` or as specific as
                `language_territory_script_variant@modifier`.

                Plugins are expected to to do their best to accommodate the given
                locale, but can fall back to a more general language variant if that is
                all it supports.  E.g. from `en_CA` to just `en`.

        Returns:
            The display name of the setting in a language appropriate for the given
                locale.  If the given locale is not supported at all, then the plugin is
                expected to return a display name in it's default language, or English
                if that is preferred.

        Raises:
            KeyError or AttributeError: If the given setting name is not a recognized
                setting.

        """

    def get_setting_description(self, setting_name: str, locale: str) -> str:
        """Return the given setting's description, appropriate for the given locale.

        Args:
            setting_name: The name of the setting as returned from
                [get_settings_spec][aquarion.libs.libtts.api.ITTSPlugin.get_settings_spec]
                mapping keys.
            locale:
                The locale should be a POSIX-compliant (i.e. using underscores) or
                CLDR-compliant (i.e. using hyphens) locale string like `en_CA`,
                `zh-Hant`, `ca-ES-valencia`, or even `de_DE.UTF-8@euro`.  It can be as
                general as `fr` or as specific as
                `language_territory_script_variant@modifier`.

                Plugins are expected to to do their best to accommodate the given
                locale, but can fall back to a more general language variant if that is
                all it supports.  E.g. from `en_CA` to just `en`.

        Returns:
            The description of the setting in a language appropriate for the given
                locale.  If the given locale is not supported at all, then the plugin is
                expected to return a description in it's default language, or English if
                that is preferred.

        Raises:
            KeyError or AttributeError: If the given setting name is not a recognized
                setting.

        """

    def get_supported_locales(self) -> AbstractSet[str]:
        """Return the set of speech locales supported by the TTS backend.

        This should also be the locales that the plugin supports for display names,
        setting names, setting descriptions, etc.

        Locales can be in either POSIX-compliant (i.e. using underscores) or
        CLDR-compliant (i.e. using hyphens) formats, and client applications are
        expected to support both.

        Returns:
            An *immutable* set of locale strings.

        Example:
            ```python
            frozenset({"fr_CA", "ca-ES-valencia", "zh-Hant"})
            ```

        Note:
            The set of locales should as be specific as is directly supported and should
            *not* include broader / more general or approximate catch-all locales unless
            they are also explicitly supported, or nothing more specific is supported.
            I.e. `en_CA` is good, `en` is bad, unless `en` is the most specific the TTS
            backend supports.  Or, if `ca-ES-valencia` is supported, then that is
            preferred over `ca-ES`.  ... In short, be as precise and honest as you can.

        """


class TTSPluginRegistry:
    """Registry of all *aquarion-libtts* backend plugins.

    TTS backends and everything related to them are created / accessed through
    [ITTSPlugin][aquarion.libs.libtts.api.ITTSPlugin] instances.  The plugin registry is
    responsible for finding, loading, listing, enabling, disabling and giving access to
    those plugins.

    """

    def __init__(self) -> None:
        self._plugins: dict[str, ITTSPlugin] = {}
        self._enabled_plugins: set[str] = set()

    def load_plugins(self, *, validate: bool = True) -> None:
        """Load all *aquarion-libtts* backend plugins.

        Plugins are discovered by searching for
        [pyproject.toml entry points](https://packaging.python.org/en/latest/specifications/pyproject-toml/#entry-points)
        named `aquarion-libtts`, then searching those entry points for hook functions
        decorated with [tts_hookimpl][aquarion.libs.libtts.api.tts_hookimpl], and
        finally calling those hook functions.  The plugins returned by those hook
        functions are then stored in the plugin registry and made accessible.

        Note:
            All plugins are disabled by default.  Use the
            [enable][aquarion.libs.libtts.api.TTSPluginRegistry.enable] method to enable
            a plugin.

        Args:
            validate: If [True][], then an exception is raised if any hook functions do
                not conform to the expected hook specification.

                If [False][], then this check is bypassed.

        Raises:
            pluggy.PluginValidationError: If `validate` is [True][] and a hook function
                does not conform to the expected specification.

        Examples:
            ```toml title="pyproject.toml"
            [project.entry-points.'aquarion-libtts']
            my_plugin_v1 = "package.hook"
            ```

            ```python title="myhookmodule.py"
            @tts_hookimpl
            def register_my_tts_plugin() -> ITTSPlugin | None:
                from package.plugin import MyTTSPlugin
                return MyTTSPlugin()
            ```

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
            only_disabled: If [True][], then only the *disabled* plugins are listed.
            list_all: If [True][], then *all* plugins are listed, regardless of their
                enabled / disabled status.

        Returns:
            The set of plugin IDs.

        Raises:
            ValueError: If both arguments are [True][].

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
        """Return the plugin the for the given ID.

        Args:
            id_: The ID of the desired, already loaded, plugin.  E.g. `kokoro_v1`.

        Returns:
            The requested plugin object.

        Raises:
            ValueError: If the given ID does not match any registered plugin.

        """
        try:
            return self._plugins[id_]
        except KeyError:
            self._raise_plugin_not_found(id_)

    def is_enabled(self, plugin_id: str) -> bool:
        """Return whether or not the requested plugin is enabled.

        Args:
            plugin_id: The ID of the plugin to check.

        Returns:
            [True][] if the plugin is enabled, [False][] otherwise.

        """
        return plugin_id in self._enabled_plugins

    def enable(self, plugin_id: str) -> None:
        """Enable a TTS plugin for inclusion in enabled plugins list.

        The idea behind enabled vs disabled plugins is that it allows one to manage
        which plugins are listed / displayed to a user, independently of all the plugins
        that are installed / loaded.  I.e. It allows for filtering which plugins one
        wants exposed and which should be kept hidden.  E.g. Some plugins could be not
        supported by your application, even though they got installed with some other
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
        """Disable a TTS plugin for exclusion in in enabled plugins list.

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
