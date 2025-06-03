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


"""TTSSpeechData Data type."""

from dataclasses import dataclass


@dataclass(kw_only=True, frozen=True, slots=True)
class TTSSpeechData:
    """A blob of speech audio along with some related metadata."""

    audio: bytes
    format: str  # E.g. "Linear PCM", "WAV", "MP3", etc.
    sample_rate: int  # E.g 8000, 24000, 48000, etc.
    sample_width: int  # E.g. 8 for 8-bit, 12 for 12-bit, 16 for 16-bit, etc.
    byte_order: str  # E.g. "Little-Endian", "LE", "big-endian", "be", etc.
    num_channels: int  # E.g. 1 for mono, 2 for stereo, etc.
