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

from collections.abc import Mapping

from loguru import logger

from aquarion.libs.libtts._kokoro._backend import KokoroBackend
from aquarion.libs.libtts._kokoro._settings import KokoroSettings
from aquarion.libs.libtts._utils import load_internal_language
from aquarion.libs.libtts.api import ITTSBackend, ITTSSettings, JSONSerializableTypes


class KokoroPlugin:
    """Aquarion libtts plugin for the Kokoro TTS backend."""

    @property
    def id(self) -> str:
        """Unique identifier for the plugin.

        The id must be unique across all Aquarion libtts plugins.
        """
        return "kokoro_v1"

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
        _, t = load_internal_language(locale)
        return _("Kokoro")

    def make_settings(
        self, from_dict: Mapping[str, JSONSerializableTypes] | None = None
    ) -> ITTSSettings:
        """Return an object that conforms to the ITTSSettings protocol.

        If `from_dict` is not None, then the given values should be used to initialize
        the settings.

        If `from_dict` is None, then default values for all settings should be used.

        This function is expected to validate it's inputs.  If any setting is invalid
        for the concrete implementation of ITTSSettings that the factory will create,
        then a KeyError, ValueError or TypeError (or subclass thereof) should be raised.
        """
        if from_dict is None:
            from_dict = {}
        # Pydantic handles the type coercion and validation.
        settings = KokoroSettings(**from_dict)  # type:ignore[arg-type]
        logger.debug(f"Created new KokoroSettings: {settings!s}")
        return settings

    def make_backend(self, settings: ITTSSettings) -> ITTSBackend:
        """Return an object that conforms to the ITTSBackend protocol.

        Custom or default settings must be provided to configure the TTS backend.

        Implementations of this interface should check that they are only getting the
        correct concrete settings class and raise TypeError if any other kind of
        concrete ITTSSettings is given.
        """
        backend = KokoroBackend(settings)
        logger.debug("Created new KokoroBackend.")
        return backend
