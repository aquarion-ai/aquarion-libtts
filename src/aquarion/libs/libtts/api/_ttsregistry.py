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


"""TTSRegistry is the central registry of all TTS backend and settings factories."""

from dataclasses import dataclass
from typing import Never, cast

from aquarion.libs.libtts.api._ttsbackend import ITTSBackendFactory
from aquarion.libs.libtts.api._ttssettings import ITTSSettings, ITTSSettingsFactory


@dataclass(frozen=True, kw_only=True)
class TTSRegistryRecord[T: ITTSSettings]:
    """Entry record to register with the TTSRegistry."""

    key: str
    display_name: str
    settings_factory: ITTSSettingsFactory[T]
    backend_factory: ITTSBackendFactory[T]


class TTSRegistry:
    """Central registry of TTS backend and settings factories.

    Each backend will register their factories here and then those factories can be
    retrieved later for use.
    """

    def __init__(self) -> None:
        self._records: dict[str, TTSRegistryRecord[ITTSSettings]] = {}
        self._enabled_backends: set[str] = set()

    def register[T: ITTSSettings](self, record: TTSRegistryRecord[T]) -> None:
        """Register a TTS backend for future use.

        Registered backends are disabled by default.  It is the library user, not the
        backend creator that is responsible for enabling the backend they want to use
        and support.
        """
        if record.key in self._records:
            existing_record = self._records[record.key]
            if record == existing_record:
                return  # Idempotent operation
            message = (
                "Key already in use by another TTS backend: "
                f" [{existing_record.display_name}]"
            )
            raise ValueError(message)
        self._records[record.key] = cast("TTSRegistryRecord[ITTSSettings]", record)

    def get_record(self, key: str) -> TTSRegistryRecord[ITTSSettings]:
        """Return the record the for the given key.

        Raises ValueError exception if the given key does not match any
        registered backend.
        """
        try:
            return self._records[key]
        except KeyError:
            self._raise_backend_not_found(key)

    def get_names(self, *, include_disabled: bool = False) -> dict[str, str]:
        """Return the keys and display names of all the registered backends."""
        return {
            record.key: record.display_name
            for record in self._records.values()
            if (record.key in self._enabled_backends) or include_disabled
        }

    def enable(self, key: str) -> None:
        """Enable a TTS backend for inclusion in .get_names().

        Raises ValueError exception if the given key does not match any
        registered backend.
        """
        if key not in self._records:
            self._raise_backend_not_found(key)
        self._enabled_backends.add(key)

    def disable(self, key: str) -> None:
        """Disable a TTS backed from inclusion in .get_names().

        Raises ValueError exception if the given key does not match any
        registered backend.
        """
        if key not in self._records:
            self._raise_backend_not_found(key)
        self._enabled_backends.discard(key)

    ## Internal methods

    def _raise_backend_not_found(self, key: str) -> Never:
        """Shared method for when a backend is not registered."""
        message = f"TTS Backend not found: [{key}]"
        raise ValueError(message)
