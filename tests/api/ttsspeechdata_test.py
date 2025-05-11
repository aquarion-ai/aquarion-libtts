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

"""Unit tests for the TTSSpeechData data type."""

from typing import Any

import pytest

from aquarion.libs.libtts.api._ttsspeechdata import TTSSpeechData

DUMMY_AUDIO = b"audio data here"
DUMMY_MIME_TYPE = "audio/wav"
DUMMY_CODEC = "MP3"
DUMMY_BPS = 192


def test_ttsspeechdata_should_accept_audio_data_as_a_keyword_argument() -> None:
    TTSSpeechData(audio=DUMMY_AUDIO, mime_type=DUMMY_MIME_TYPE)


def test_ttsspeechdata_should_accept_a_mime_type_as_a_keyword_argument() -> None:
    TTSSpeechData(audio=DUMMY_AUDIO, mime_type=DUMMY_MIME_TYPE)


def test_ttsspeechdata_should_accept_a_codec_as_a_keyword_argument() -> None:
    TTSSpeechData(audio=DUMMY_AUDIO, mime_type=DUMMY_MIME_TYPE, codec=DUMMY_CODEC)


def test_ttsspeechdata_should_accept_bps_as_a_keyword_argument() -> None:
    TTSSpeechData(audio=DUMMY_AUDIO, mime_type=DUMMY_MIME_TYPE, bps=DUMMY_BPS)


def test_ttsspeechdata_should_require_audio_data() -> None:
    with pytest.raises(TypeError, match="missing .* required keyword-only argument"):
        TTSSpeechData()  # type: ignore [call-arg]


def test_ttsspeechdata_should_require_a_mime_type() -> None:
    with pytest.raises(TypeError, match="missing .* required keyword-only argument"):
        TTSSpeechData(audio=DUMMY_AUDIO)  # type: ignore [call-arg]


def test_ttsspeechdata_should_require_all_keyword_arguments() -> None:
    with pytest.raises(
        TypeError, match="takes .* positional argument but .* were given"
    ):
        TTSSpeechData(  # type: ignore [misc]
            DUMMY_AUDIO,
            DUMMY_MIME_TYPE,
            DUMMY_CODEC,
            DUMMY_BPS,
        )


@pytest.mark.parametrize(  # type: ignore [misc]
    ("attribute", "expected"),
    [
        ("audio", DUMMY_AUDIO),
        ("mime_type", DUMMY_MIME_TYPE),
        ("codec", DUMMY_CODEC),
        ("bps", DUMMY_BPS),
    ],
)
def test_ttsspeechdata_should_store_all_given_values(  # type: ignore [explicit-any,misc]
    attribute: str,
    expected: Any,  # noqa: ANN401
) -> None:
    speech_data = TTSSpeechData(
        audio=DUMMY_AUDIO, mime_type=DUMMY_MIME_TYPE, codec=DUMMY_CODEC, bps=DUMMY_BPS
    )
    assert getattr(speech_data, attribute) == expected  # type: ignore [misc]


@pytest.mark.parametrize(
    "attribute",
    [
        "codec",
        "bps",
    ],
)
def test_ttsspeechdata_optional_values_should_be_none_when_not_specified(
    attribute: str,
) -> None:
    speech_data = TTSSpeechData(audio=DUMMY_AUDIO, mime_type=DUMMY_MIME_TYPE)
    assert getattr(speech_data, attribute) is None  # type: ignore [misc]


@pytest.mark.parametrize(  # type: ignore [misc]
    ("attribute", "new_value"),
    [
        ("audio", DUMMY_AUDIO),
        ("mime_type", DUMMY_MIME_TYPE),
        ("codec", DUMMY_CODEC),
        ("bps", DUMMY_BPS),
    ],
)
def test_ttsspeechdata_attributes_should_be_immutable(  # type: ignore [explicit-any,misc]
    attribute: str,
    new_value: Any,  # noqa: ANN401
) -> None:
    speech_data = TTSSpeechData(
        audio=DUMMY_AUDIO, mime_type=DUMMY_MIME_TYPE, codec=DUMMY_CODEC, bps=DUMMY_BPS
    )
    with pytest.raises(AttributeError, match="cannot assign to field"):
        setattr(speech_data, attribute, new_value)  # type: ignore [misc]


def test_ttsspeechdata_should_not_accept_additional_attributes() -> None:
    speech_data = TTSSpeechData(audio=DUMMY_AUDIO, mime_type=DUMMY_MIME_TYPE)
    # This exception message is really cryptic and unhelpful.  But the effect works.
    with pytest.raises(TypeError, match="is not an instance or subtype of type"):
        speech_data.new_custom_attribute = "new value"  # type: ignore [attr-defined]
