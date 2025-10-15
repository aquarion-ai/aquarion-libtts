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


"""Kokoro TTS plugin implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from aquarion.libs.libtts._utils import load_internal_language
from aquarion.libs.libtts.kokoro._backend import KokoroBackend
from aquarion.libs.libtts.kokoro.settings import KokoroLocales, KokoroSettings

if TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import Set as AbstractSet

    from aquarion.libs.libtts.api import (
        ITTSBackend,
        ITTSSettings,
        JSONSerializableTypes,
        TTSSettingsSpecEntry,
        TTSSettingsSpecEntryTypes,
    )


class KokoroPlugin:
    """Aquarion libtts plugin for the Kokoro TTS backend."""

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
        return "kokoro_v1"

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
        _, _t = load_internal_language(locale)
        return _("Kokoro")

    def make_settings(
        self, from_dict: Mapping[str, JSONSerializableTypes] | None = None
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
        if from_dict is None:
            from_dict = {}
        # Pydantic handles the type coercion and validation.
        settings = KokoroSettings(**from_dict)  # type:ignore[arg-type]
        logger.debug(f"Created new KokoroSettings: {settings!s}")
        return settings

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
        backend = KokoroBackend(settings)
        logger.debug("Created new KokoroBackend.")
        return backend

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
        return KokoroSettings._make_spec()  # noqa: SLF001

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
        _, _t = load_internal_language(locale)
        return _(KokoroSettings._get_setting_display_name(setting_name))  # noqa: SLF001

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
        _, _t = load_internal_language(locale)
        return _(KokoroSettings._get_setting_description(setting_name))  # noqa: SLF001

    def get_supported_locales(self) -> AbstractSet[str]:
        """Return the set of locales supported by the TTS backend for speaking.

        This should also be the locales that the plugin supports for display names,
        setting names, setting descriptions, etc.

        Locales can be in either POSIX-compliant (i.e. using underscores) or
        CLDR-compliant (i.e. using hyphens) formats, and client applications are
        expected to support both.

        Returns:
            An *immutable* set of locale strings.

        Example:
            .. code:: python

            frozenset({"fr_CA", "ca-ES-valencia", "zh-Hant"})

        Note:
            The set of locales should as be specific as is directly supported and should
            *not* include broader / more general or approximate catch-all locales unless
            they are also explicitly supported, or nothing more specific is supported.
            I.e. ``en_CA`` is good, ``en`` is bad, unless ``en`` is as specific as the
            TTS backend supports.  Or if ``ca-ES-valencia`` is supported, then that is
            preferred over ``ca-ES``.  ... In short, be as precise and honest as you
            can.

        """
        return frozenset(str(locale) for locale in KokoroLocales)
