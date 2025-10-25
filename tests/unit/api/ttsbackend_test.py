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


"""Unit tests for api._ttsbackend.

These tests serve mostly to document the expectations of all TTSBackend implementations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from aquarion.libs.libtts.api._ttsbackend import (
    ITTSBackend,
    TTSAudioSpec,
    TTSSampleByteOrders,
    TTSSampleTypes,
)
from aquarion.libs.libtts.api._ttssettings import ITTSSettings
from tests.unit.api.ttssettings_test import (
    AnotherTTSSettings,
    DummyTTSSettings,
    DummyTTSSettingsHolder,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

type TTSAudioSpecTypes = bytes | str | int

AUDIO_SPEC_REQUIRED_ARGS: Final = {
    "mime_type": "audio/L16",
    "sample_rate": 24000,
    "sample_type": "s",
    "sample_width": 16,
    "byte_order": "big-endian",
    "num_channels": 1,
}


### TTSAudioSpec Tests ###


def test_ttsaudiospec_should_accept_required_arguments_as_keyword_arguments() -> None:
    TTSAudioSpec(**AUDIO_SPEC_REQUIRED_ARGS)  # type:ignore[arg-type]


@pytest.mark.parametrize("argument", AUDIO_SPEC_REQUIRED_ARGS)
def test_ttsaudiospec_should_require_required_arguments(argument: str) -> None:
    arguments = AUDIO_SPEC_REQUIRED_ARGS.copy()
    del arguments[argument]
    with pytest.raises(TypeError, match=r"missing .* required keyword-only argument"):
        TTSAudioSpec(**arguments)  # type:ignore[arg-type]


def test_ttsaudiospec_should_require_all_keyword_arguments() -> None:
    with pytest.raises(
        TypeError, match=r"takes .* positional argument.? but .* were given"
    ):
        TTSAudioSpec(*AUDIO_SPEC_REQUIRED_ARGS.values())  # type:ignore[call-arg]


@pytest.mark.parametrize(("attribute", "expected"), AUDIO_SPEC_REQUIRED_ARGS.items())
def test_ttsaudiospec_should_store_all_given_values(
    attribute: str,
    expected: TTSAudioSpecTypes,
) -> None:
    speech_data = TTSAudioSpec(**AUDIO_SPEC_REQUIRED_ARGS)  # type:ignore[arg-type]
    assert getattr(speech_data, attribute) == expected  # type:ignore[misc]


@pytest.mark.parametrize(("attribute", "new_value"), AUDIO_SPEC_REQUIRED_ARGS.items())
def test_ttsaudiospec_attributes_should_be_immutable(
    attribute: str,
    new_value: TTSAudioSpecTypes,
) -> None:
    speech_data = TTSAudioSpec(**AUDIO_SPEC_REQUIRED_ARGS)  # type:ignore [arg-type]
    with pytest.raises(AttributeError, match="cannot assign to field"):
        setattr(speech_data, attribute, new_value)


def test_ttsaudiospec_should_not_accept_additional_attributes() -> None:
    speech_data = TTSAudioSpec(**AUDIO_SPEC_REQUIRED_ARGS)  # type:ignore[arg-type]
    # This exception message is really cryptic and unhelpful.  But the effect works.
    with pytest.raises(TypeError, match="an instance or subtype of type"):
        speech_data.new_custom_attribute = "new value"  # type:ignore[attr-defined]


### ITTSBackend Tests ###


class DummyTTSBackend(DummyTTSSettingsHolder):
    """Dummy TTS Backend to test the protocol.

    Specific implementations here do not matter, the only important thing is to conform
    to the ITTSBackend protocol.
    """

    def __init__(self) -> None:
        super().__init__()
        self._is_started = False

    @property
    def audio_spec(self) -> TTSAudioSpec:
        return TTSAudioSpec(
            mime_type="audio/L16",
            sample_rate=24000,
            sample_type=TTSSampleTypes.SIGNED_INT,
            sample_width=16,
            byte_order=TTSSampleByteOrders.BIG_ENDIAN,
            num_channels=1,
        )

    @property
    def is_started(self) -> bool:
        return self._is_started

    def convert(self, text: str) -> Iterator[bytes]:
        if not self.is_started:
            message = "Backend is not started"
            raise RuntimeError(message)
        yield f"some audio of {text}".encode()

    def start(self) -> None:
        self._is_started = True

    def stop(self) -> None:
        self._is_started = False


def test_ittsbackend_should_conform_to_its_protocol() -> None:
    backend = DummyTTSBackend()
    _: ITTSBackend = backend  # Typecheck protocol conformity
    assert isinstance(backend, ITTSBackend)  # Runtime check as well


def test_ittsbackend_should_be_stopped_by_default() -> None:
    backend = DummyTTSBackend()
    assert not backend.is_started


## .get_settings tests


def test_ittsbackend_get_settings_should_return_an_ittssettings() -> None:
    backend = DummyTTSBackend()
    settings = backend.get_settings()
    _: ITTSSettings = settings  # Typecheck protocol conformity
    assert isinstance(settings, ITTSSettings)  # Runtime check as well


## .update_settings tests


def test_ittsbackend_update_settings_should_accept_a_settings_argument() -> None:
    backend = DummyTTSBackend()
    backend.update_settings(DummyTTSSettings())


def test_ittsbackend_update_settings_should_require_the_settings_argument() -> None:
    backend = DummyTTSBackend()
    with pytest.raises(TypeError, match=r"missing .* required positional argument"):
        backend.update_settings()  # type:ignore[call-arg]


def test_ittsbackend_update_settings_should_not_return_anything() -> None:
    # CQS principle: Commands should not return anything.
    backend = DummyTTSBackend()
    result: None = backend.update_settings(DummyTTSSettings())  # type:ignore[func-returns-value]
    assert result is None


def test_ittsbackend_update_settings_should_update_the_settings() -> None:
    backend = DummyTTSBackend()
    orig_settings = backend.get_settings()
    new_settings = DummyTTSSettings(attr1="new settings")
    backend.update_settings(new_settings)
    updated_settings = backend.get_settings()
    assert updated_settings == new_settings
    assert updated_settings != orig_settings


def test_ittsbackend_update_settings_should_raise_error_if_incorrect_kind() -> None:
    backend = DummyTTSBackend()
    incorrect_settings = AnotherTTSSettings()
    with pytest.raises(TypeError, match="Incorrect settings type"):
        backend.update_settings(incorrect_settings)


## .audio_spec tests


def test_ittsbackend_should_have_an_audio_spec_property() -> None:
    backend = DummyTTSBackend()
    assert hasattr(backend, "audio_spec")


def test_ittsbackend_audio_spec_should_return_a_ttsaudiospec_instance() -> None:
    backend = DummyTTSBackend()
    assert isinstance(backend.audio_spec, TTSAudioSpec)


## .convert() tests


def test_ittsbackend_convert_should_require_some_text_input() -> None:
    backend = DummyTTSBackend()
    with pytest.raises(TypeError, match=r"missing .* required positional argument"):
        backend.convert()  # type:ignore[call-arg]


def test_ittsbackend_convert_should_return_a_generator_of_chunks_of_audio_bytes() -> (
    None
):
    text = "some text"
    expected_audio = f"some audio of {text}".encode()
    backend = DummyTTSBackend()
    backend.start()
    audio_bytes = b"".join(list(backend.convert(text)))
    assert audio_bytes == expected_audio


def test_ittsbackend_convert_should_raise_an_error_if_backend_not_started() -> None:
    backend = DummyTTSBackend()
    with pytest.raises(RuntimeError, match="Backend is not started"):
        list(backend.convert("some text"))


## .is_started tests


def test_ittsbackend_is_started_should_return_true_if_started() -> None:
    backend = DummyTTSBackend()
    backend.start()
    assert backend.is_started


def test_ittsbackend_is_started_should_return_false_if_stopped() -> None:
    backend = DummyTTSBackend()
    backend.start()
    backend.stop()
    assert not backend.is_started


def test_ittsbackend_is_started_should_be_read_only() -> None:
    backend = DummyTTSBackend()
    with pytest.raises(AttributeError, match=r"property .* of .* object has no setter"):
        backend.is_started = True  # type:ignore[misc]


## .start() tests


def test_ittsbackend_start_should_start_the_backend() -> None:
    backend = DummyTTSBackend()
    backend.start()
    assert backend.is_started


def test_ittsbackend_start_should_be_idempotent() -> None:
    backend = DummyTTSBackend()
    backend.start()
    assert backend.is_started
    backend.start()
    assert backend.is_started


def test_ittsbackend_start_should_not_return_anything() -> None:
    # CQS principle: Commands should not return anything.
    backend = DummyTTSBackend()
    result: None = backend.start()  # type:ignore[func-returns-value]
    assert result is None


## .stop() tests


def test_ittsbackend_stop_should_stop_the_backend() -> None:
    backend = DummyTTSBackend()
    backend.start()
    assert backend.is_started
    backend.stop()
    assert not backend.is_started


def test_ittsbackend_stop_should_be_idempotent() -> None:
    backend = DummyTTSBackend()
    backend.start()
    assert backend.is_started
    backend.stop()
    assert not backend.is_started
    backend.stop()  # type:ignore[unreachable]  # The type checker is wrong.  Tested.
    assert not backend.is_started


def test_ittsbackend_stop_should_not_return_anything() -> None:
    # CQS principle: Commands should not return anything.
    backend = DummyTTSBackend()
    result: None = backend.stop()  # type:ignore[func-returns-value]
    assert result is None
