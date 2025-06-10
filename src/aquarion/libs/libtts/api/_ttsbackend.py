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

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from aquarion.libs.libtts.api._ttssettings import ITTSSettingsHolder


@dataclass(kw_only=True, frozen=True, slots=True)
class TTSAudioSpec:
    """Audio metadata about the speed audio that an ITTSBackend returns."""

    format: str  # E.g. "Linear PCM", "WAV", "MP3", etc.
    sample_rate: int  # E.g 8000, 24000, 48000, etc.
    sample_width: int  # E.g. 8 for 8-bit, 12 for 12-bit, 16 for 16-bit, etc.
    byte_order: str  # E.g. "Little-Endian", "LE", "big-endian", "be", etc.
    num_channels: int  # E.g. 1 for mono, 2 for stereo, etc.


@runtime_checkable
class ITTSBackend(ITTSSettingsHolder, Protocol):
    """Common interface for all TTS backends."""

    @property
    def audio_spec(self) -> TTSAudioSpec:
        """Return metadata about the speech audio format.

        E.g. Mono 16-bit little-endian linear PCM audio at 24KHz.
        """

    @property
    def is_started(self) -> bool:
        """Return True if TTS backend is started / running, False otherwise."""

    def convert(self, text: str) -> Iterator[bytes]:
        """Return speech audio for the given text as one or more chunks of bytes.

        The audio data must be in the same format as specified in .audio_spec.
        """

    def start(self) -> None:
        """Start the TTS backend.

        If the backend is already started, this method should be idempotent.
        """

    def stop(self) -> None:
        """Stop the TTS backend.

        If the backend is already stopped, this method should be idempotent.
        """
