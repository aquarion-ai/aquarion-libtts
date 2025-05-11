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

    def __eq__(self, other: object) -> bool:
        """Return True if all settings values match."""

    def to_dict(self) -> dict[str, Any]:  # type: ignore [explicit-any]
        """Export all settings as a dictionary of only built-in Python types."""

    def validate(self) -> None:
        """Validate all settings."""

    def is_valid(self) -> bool:
        """Return True if all settings are valid."""


@runtime_checkable
class ITTSSettingsFactory[T: ITTSSettings](Protocol):
    """Common interface for all TTSSettings factories."""

    @staticmethod
    def __call__(
        from_dict: Mapping[str, JSONSerializableTypes] | None = None,
    ) -> T:
        """Return an object that conforms to the ITTSSettings protocol.

        If `from_dict` is not None, then the given values should be used to initialize
        the settings.

        If `from_dict` is None, then default values for all settings should be used.
        """


@runtime_checkable
class ITTSSettingsHolder[T: ITTSSettings](Protocol):
    """Common interface for objects that accept and contain ITTSSettings."""

    @property
    def settings(self) -> T:
        """Return the current settings for the TTS backend."""

    @settings.setter
    def settings(self, new_settings: T) -> None:
        """Store and apply the new given settings to the TTS backend."""


@runtime_checkable
class ITTSSettingsHolderFactory[T: ITTSSettings](Protocol):
    """Common interface for all ITTSSettingsHolderFactory factories."""

    @staticmethod
    def __call__(settings: T) -> Any:  # type: ignore [explicit-any,misc] # noqa: ANN401
        """Return an object that conforms to the ITTSSettingsHolder protocol.

        If `settings` is not None, then the given settings should be stored and used.

        If `settings` is None, then default settings should be used.
        """
