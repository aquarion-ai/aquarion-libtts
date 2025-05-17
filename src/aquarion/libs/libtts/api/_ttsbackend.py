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


"""TTSBackend protocol."""

from typing import Protocol, runtime_checkable

from aquarion.libs.libtts.api._ttssettings import ITTSSettingsHolder
from aquarion.libs.libtts.api._ttsspeechdata import TTSSpeechData


@runtime_checkable
class ITTSBackend(ITTSSettingsHolder, Protocol):
    """Common interface for all TTS backends."""

    def convert(self, text: str) -> TTSSpeechData:
        """Return speech audio generated from the given text."""

    @property
    def is_started(self) -> bool:
        """Return True if TTS backend is started / running, False otherwise."""

    def start(self) -> None:
        """Start the TTS backend.

        If the backend is already started, this method should be idempotent.
        """

    def stop(self) -> None:
        """Stop the TTS backend.

        If the backend is already stopped, this method should be idempotent.
        """
