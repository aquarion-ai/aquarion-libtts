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
class TTSSettings(Protocol):
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
class TTSSettingsFactory(Protocol):
    """Common interface for all TTSSettings factories."""

    @staticmethod
    def __call__(
        from_dict: Mapping[str, JSONSerializableTypes] | None = None,
    ) -> TTSSettings:
        """Return an object that conforms to the TTSSettings protocol.

        If `from_dict` is not None, then the given values will be used to initialize the
        settings.

        If `from_dict` is None, then default values for all settings will be used.
        """
