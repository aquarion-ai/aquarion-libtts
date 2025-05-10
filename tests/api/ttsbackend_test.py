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


"""Unit tests for the TTSBackend protocol.

These tests serve mostly to document the expectations of all TTSBackend implementations.
"""

import pytest

from aquarion.libs.libtts.api.ttsbackend import ITTSBackend
from aquarion.libs.libtts.api.ttsspeechdata import TTSSpeechData


class DummyTTSBackend:
    """Dummy TTS Backend to test the protocol.

    Specific implementations here do not matter, the only important thing is to conform
    to the TTSSettings protocol.
    """

    def convert(self, text: str) -> TTSSpeechData:
        return TTSSpeechData(
            audio=f"some audio of {text}".encode(), mime_type="audio/wav"
        )


def test_ittsbackend_should_conform_to_its_protocol() -> None:
    backend = DummyTTSBackend()
    _: ITTSBackend = backend  # Typecheck protocol conformity
    assert isinstance(backend, ITTSBackend)  # Runtime check as well


def test_ttsbackend_convert_should_require_some_text_input() -> None:
    backend = DummyTTSBackend()
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        backend.convert()  # type: ignore [call-arg]


def test_ttsbackend_convert_should_return_a_ttsspeechdata_object() -> None:
    backend = DummyTTSBackend()
    speech_data = backend.convert("some text")
    assert isinstance(speech_data, TTSSpeechData)
