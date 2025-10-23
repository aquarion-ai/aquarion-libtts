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

    Note:
        The string values of these types match
        [FFmpeg's format descriptions](https://trac.ffmpeg.org/wiki/audio%20types), in
        case that is ever useful.

    """

    SIGNED_INT = "s"
    """Signed integer samples. (I.e. positive and negative numbers allowed.)"""

    UNSIGNED_INT = "u"
    """Unsigned integer samples. (I.e. only positive numbers, but with more values.)"""

    FLOAT = "f"
    """Floating point samples."""


class TTSSampleByteOrders(StrEnum):
    """The byte order for multi-byte audio samples.

    Note:
        The string values of these types match
        [FFmpeg's format descriptions](https://trac.ffmpeg.org/wiki/audio%20types), in
        case that is ever useful.

    """

    BIG_ENDIAN = "be"
    """The most significant byte is stored first, then the least significant byte."""

    LITTLE_ENDIAN = "le"
    """The least significant byte is stored first, then the most significant byte."""

    NOT_APPLICABLE = ""
    """This should only be used for 8-bit (i.e. single byte) samples."""


@dataclass(kw_only=True, frozen=True, slots=True)
class TTSAudioSpec:
    """Metadata about an audio format.

    This describes the audio format that an
    [ITTSBackend][aquarion.libs.libtts.api.ITTSBackend] returns.

    Note:
        Instances of this class are immutable once created.

    """

    format: str
    """E.g. "Linear PCM", "WAV", "MP3", etc."""

    sample_rate: int
    """E.g 8000, 24000, 48000, etc."""

    sample_type: TTSSampleTypes
    """E.g. Signed Integer, Unsigned Integer or Floating Point."""

    sample_width: int
    """E.g. 8 for 8-bit, 12 for 12-bit, 16 for 16-bit, etc."""

    byte_order: TTSSampleByteOrders
    """E.g. Little Endian or Big Endian."""

    num_channels: int
    """E.g. 1 for mono, 2 for stereo, etc."""


@runtime_checkable
class ITTSBackend(ITTSSettingsHolder, Protocol):
    """Common interface for all TTS backends.

    An `ITTSBackend`  is responsible for converting text in to a stream of speech audio
    chunks.  To do this, it should first be started with the
    [start][aquarion.libs.libtts.api.ITTSBackend.start] method, then the
    [convert][aquarion.libs.libtts.api.ITTSBackend.convert] method can be used to do any
    number of text to speech conversions, and finally it should be shut down with the
    [stop][aquarion.libs.libtts.api.ITTSBackend.stop] method when no longer needed.

    An `ITTSBackend` is also responsible for reporting the kind of audio that it
    produces (e.g. raw PCM, WAVE, MP3, OGG, VP8, stereo, mono, 8-bit, 16-bit, etc.).
    This is reported via the
    [audio_spec][aquarion.libs.libtts.api.ITTSBackend.audio_spec] attribute.

    Lastly, since each `ITTSBackend` is also an
    [ITTSSettingsHolder][aquarion.libs.libtts.api.ITTSSettingsHolder], then it must
    also accept configuration settings.  These are commonly provided at instantiation,
    but that is not strictly required to conform to the
    [ITTSSettingsHolder][aquarion.libs.libtts.api.ITTSSettingsHolder] protocol.

    """

    @property
    def audio_spec(self) -> TTSAudioSpec:
        """Metadata about the speech audio format.

        E.g. Mono 16-bit little-endian linear PCM audio at 24KHz.

        Returns:
            The audio output format emitted by the
                [convert][aquarion.libs.libtts.api.ITTSBackend.convert] method.

        Note:
            This should be a read-only property.

        """

    @property
    def is_started(self) -> bool:
        """Whether or not the backend already started.

        Returns:
            [True][] if the backend is started, [False][] otherwise.

        Note:
            This should be a read-only property.

        """

    def convert(self, text: str) -> Iterator[bytes]:
        """Return speech audio for the given text as one or more binary chunks.

        Args:
            text: The text to convert in to speech.

        Returns:
            An [Iterator][collections.abc.Iterator] of chunks of audio in the format
                specified by
                [audio_spec][aquarion.libs.libtts.api.ITTSBackend.audio_spec].

        """

    def start(self) -> None:
        """Start the TTS backend.

        Note:
            If the backend is already started, this method should be idempotent and do
            nothing.

        """

    def stop(self) -> None:
        """Stop the TTS backend.

        Note:
            If the backend is already started, this method should be idempotent and do
            nothing.

        """
