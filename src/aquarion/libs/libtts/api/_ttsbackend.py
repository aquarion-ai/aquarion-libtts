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

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from aquarion.libs.libtts.api._ttssettings import ITTSSettingsHolder

if TYPE_CHECKING:
    from collections.abc import Iterator


class TTSSampleTypes(StrEnum):
    """The data type of a single audio sample.

    The string values of these types match
    `FFmpeg's format descriptions <https://trac.ffmpeg.org/wiki/audio%20types>`__.

    """

    #: Signed integer samples. (I.e. positive and negative numbers allowed.)
    SIGNED_INT = "s"
    #: Unsigned integer samples. (I.e. only positive numbers, but wider sample space.)
    UNSIGNED_INT = "u"
    #: Floating point samples.
    FLOAT = "f"


@dataclass(kw_only=True, frozen=True, slots=True)
class TTSAudioSpec:
    """Audio metadata about the audio format that an :class:`ITTSBackend` returns.

    **Note:** Instances of this class are immutable once created.

    """

    #: E.g. "Linear PCM", "WAV", "MP3", etc.
    format: str
    #: E.g 8000, 24000, 48000, etc.
    sample_rate: int
    #: E.g. signed int, unsigned int or float.
    sample_type: TTSSampleTypes
    #: E.g. 8 for 8-bit, 12 for 12-bit, 16 for 16-bit, etc.
    sample_width: int
    #: E.g. "Little-Endian", "LE", "big-endian", "be", etc.
    #:
    #: **Note:** There is no standard for this but Ffmpeg uses ``be`` and ``le`` so
    #: maybe it is worth sticking with those.
    byte_order: str
    #: E.g. 1 for mono, 2 for stereo, etc.
    num_channels: int


@runtime_checkable
class ITTSBackend(ITTSSettingsHolder, Protocol):
    """Common interface for all TTS backends.

    An ITTSBackend is responsible for converting text in to speech audio stream chunks.
    To do this, it should first be started with :meth:`start`, then :meth:`convert`
    can be used to do any number of conversions, and finally it should be shut down with
    :meth:`stop` when no longer needed.

    An ITTSBackend is also responsible for reporting the kind of audio that it produces
    (e.g. raw PCM, WAVE, MP3, OGG, VP8, stereo, mono, 8-bit, 16-bit, etc.).  This is
    reported via the :attr:`audio_spec` attribute.

    Lastly, since each ITTSBackend is also an :class:`ITTSSettingsHolder`, then it must
    also accept configuration settings.  These are commonly provided at instantiation,
    but that is not strictly required to conform to the :class:`ITTSSettingsHolder`
    protocol.

    """

    @property
    def audio_spec(self) -> TTSAudioSpec:
        """Metadata about the speech audio format.

        E.g. Mono 16-bit little-endian linear PCM audio at 24KHz.

        This should be read-only.

        """

    @property
    def is_started(self) -> bool:
        """True if TTS backend is started, False otherwise.

        This should be read-only.

        """

    def convert(self, text: str) -> Iterator[bytes]:
        """Return speech audio for the given text as one or more binary chunks.

        Args:
            text: The text to convert in to speech.

        Returns:
            An :class:`~collections.abc.Iterator` of chunks of audio in the format
            specified by :attr:`audio_spec`.

        """

    def start(self) -> None:
        """Start the TTS backend.

        If the backend is already started, this method should be idempotent and do
        nothing.

        """

    def stop(self) -> None:
        """Stop the TTS backend.

        If the backend is already started, this method should be idempotent and do
        nothing.

        """
