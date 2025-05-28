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


"""TTSSettings protocol."""

from collections.abc import Mapping, Sequence
from typing import Any, Protocol, runtime_checkable

type JSONSerializableTypes = (
    str
    | int
    | float
    | bool
    | None
    | Sequence[JSONSerializableTypes]
    | Mapping[str, JSONSerializableTypes]
)


@runtime_checkable
class ITTSSettings(Protocol):
    """Common interface for all TTS backend settings."""

    # The locale should be a POSIX-compliant locale string like `en_CA`, `zh-Hant`,
    # `ca-ES-valencia`, or even `de_DE.UTF-8@euro`.  It can be a general as `fr` or as
    # specific as `language_territory_script_variant@modifier`.
    #
    # Settings holders are expected to to do their best to accommodate the given locale,
    # but can fall back to more a general language variant if required.  E.g. from
    # `en_CA` to `en`.
    #
    # If the given locale is not supported at all, then the settings holder is expected
    # to use it's default locale instead.
    locale: str

    def __eq__(self, other: object) -> bool:
        """Return True if all settings values match."""

    def to_dict(self) -> dict[str, Any]:  # type: ignore [explicit-any]
        """Export all settings as a dictionary of only built-in Python types."""


@runtime_checkable
class ITTSSettingsHolder(Protocol):
    """Common interface for objects that accept and contain ITTSSettings."""

    def get_settings(self) -> ITTSSettings:
        """Return the current setting in use."""

    def update_settings(self, new_settings: ITTSSettings) -> None:
        """Update to the new given settings.

        Implementations of this interface should check that they are only getting the
        correct concrete settings class and raise TypeError if any other kind of
        concrete ITTSSettings is given.
        """
