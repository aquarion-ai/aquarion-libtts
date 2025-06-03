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

"""Unit tests for api._ttsspeechdata."""

from typing import Any, Final

import pytest

from aquarion.libs.libtts.api._ttsspeechdata import TTSSpeechData

REQUIRED_ARGS: Final = {
    "audio": b"audio data here",
    "format": "WAV",
    "sample_rate": 24000,
    "sample_width": 16,
    "byte_order": "little-endian",
    "num_channels": 1,
}


def test_ttsspeechdata_should_accept_required_arguments_as_keyword_arguments() -> None:
    TTSSpeechData(**REQUIRED_ARGS)  # type:ignore[arg-type]


@pytest.mark.parametrize("argument", REQUIRED_ARGS)
def test_ttsspeechdata_should_require_audio_data(argument: str) -> None:
    arguments = REQUIRED_ARGS.copy()
    del arguments[argument]
    with pytest.raises(TypeError, match="missing .* required keyword-only argument"):
        TTSSpeechData(**arguments)  # type:ignore[arg-type]


def test_ttsspeechdata_should_require_all_keyword_arguments() -> None:
    with pytest.raises(
        TypeError, match="takes .* positional argument.? but .* were given"
    ):
        TTSSpeechData(*REQUIRED_ARGS.values())  # type:ignore[call-arg]


@pytest.mark.parametrize(("attribute", "expected"), REQUIRED_ARGS.items())  # type:ignore[misc]
def test_ttsspeechdata_should_store_all_given_values(  # type:ignore[explicit-any,misc]
    attribute: str,
    expected: Any,  # noqa: ANN401
) -> None:
    speech_data = TTSSpeechData(**REQUIRED_ARGS)  # type:ignore[arg-type]
    assert getattr(speech_data, attribute) == expected  # type:ignore[misc]


@pytest.mark.parametrize(("attribute", "new_value"), REQUIRED_ARGS.items())  # type:ignore[misc]
def test_ttsspeechdata_attributes_should_be_immutable(  # type:ignore[explicit-any,misc]
    attribute: str,
    new_value: Any,  # noqa: ANN401
) -> None:
    speech_data = TTSSpeechData(**REQUIRED_ARGS)  # type:ignore [arg-type]
    with pytest.raises(AttributeError, match="cannot assign to field"):
        setattr(speech_data, attribute, new_value)  # type:ignore[misc]


def test_ttsspeechdata_should_not_accept_additional_attributes() -> None:
    speech_data = TTSSpeechData(**REQUIRED_ARGS)  # type:ignore[arg-type]
    # This exception message is really cryptic and unhelpful.  But the effect works.
    with pytest.raises(TypeError, match="must be an instance or subtype of type"):
        speech_data.new_custom_attribute = "new value"  # type:ignore[attr-defined]
