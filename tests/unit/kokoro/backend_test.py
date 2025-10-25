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

"""Unit tests for kokoro._backend module."""

from __future__ import annotations

from os import environ
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
import torch
from kokoro.pipeline import KPipeline
from logot import Logot, logged

from aquarion.libs.libtts.api import (
    ITTSBackend,
    ITTSSettings,
    TTSAudioSpec,
)
from aquarion.libs.libtts.kokoro._backend import _TEXT_IN_LOG_MAX_LEN, KokoroBackend
from aquarion.libs.libtts.kokoro.settings import KokoroSettings, KokoroVoices
from tests.unit.api.ttssettings_test import AnotherTTSSettings

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from tests.unit.kokoro.conftest import SettingsDict

EXPECTED_AUDIO_SPEC = (
    "TTSAudioSpec(mime_type='audio/L16;rate=24000;channels=1', sample_rate=24000,"
    " sample_type=<TTSSampleTypes.SIGNED_INT: 's'>, sample_width=16,"
    " byte_order=<TTSSampleByteOrders.BIG_ENDIAN: 'be'>, num_channels=1)"
)


@pytest.fixture(autouse=True)
def mock_kpipeline(mocker: MockerFixture) -> None:
    # If this environment variable is set, do not mock anything.  This is only for
    # debugging tests.  Use acceptance tests to test the actual Kokoro backend.
    if environ.get("KOKORO_TEST_SKIP_MOCK", "0") == "1":  # pragma: no cover
        return
    mock_audio_result: KPipeline.Result = mocker.MagicMock(spec_set=KPipeline.Result)
    mock_audio_result.audio = cast("torch.FloatTensor", torch.zeros(1, 2))  # type:ignore[misc]
    mock_no_audio_result: KPipeline.Result = mocker.MagicMock(spec_set=KPipeline.Result)
    mock_no_audio_result.audio = None  # type:ignore[misc]
    call_return_value: list[KPipeline.Result] = [
        mock_no_audio_result,
        mock_audio_result,
    ]
    mocker.patch.object(KPipeline, "__init__", return_value=None)
    mocker.patch.object(KPipeline, "load_voice", return_value=None)
    mocker.patch.object(KPipeline, "__call__", return_value=call_return_value)


### KokoroBackend Tests ###


def test_kokorobackend_should_accept_a_settings_argument() -> None:
    KokoroBackend(settings=KokoroSettings())


def test_kokorobackend_should_accept_settings_as_a_positional_argument() -> None:
    KokoroBackend(KokoroSettings())


def test_kokorobackend_should_require_the_settings_argument() -> None:
    with pytest.raises(TypeError, match=r"missing .* required positional argument"):
        KokoroBackend()  # type:ignore[call-arg]


def test_kokorobackend_should_require_settings_to_be_instance_of_kokorosettings() -> (
    None
):
    with pytest.raises(TypeError, match="Incorrect settings type"):
        KokoroBackend(settings=AnotherTTSSettings)  # type:ignore[arg-type]


def test_kokorobackend_should_use_local_model_path_when_given(
    real_settings_path_args: SettingsDict, mocker: MockerFixture
) -> None:
    expected = Path(cast("str", real_settings_path_args["model_path"]))
    mock_kmodel = mocker.patch("aquarion.libs.libtts.kokoro._backend.KModel")
    backend = KokoroBackend(KokoroSettings(model_path=expected))
    backend.start()
    assert mock_kmodel.call_count == 1
    assert mock_kmodel.call_args.kwargs["model"] == expected  # type:ignore[misc]


def test_kokorobackend_should_use_local_config_path_when_given(
    real_settings_path_args: SettingsDict, mocker: MockerFixture
) -> None:
    expected = Path(cast("str", real_settings_path_args["config_path"]))
    mock_kmodel = mocker.patch("aquarion.libs.libtts.kokoro._backend.KModel")
    backend = KokoroBackend(KokoroSettings(config_path=expected))
    backend.start()
    assert mock_kmodel.call_count == 1
    assert mock_kmodel.call_args.kwargs["config"] == expected  # type:ignore[misc]


def test_kokorobackend_should_use_local_voice_path_when_given(
    real_settings_path_args: SettingsDict, mocker: MockerFixture
) -> None:
    expected = Path(cast("str", real_settings_path_args["voice_path"]))
    mock_kpipeline = mocker.patch("aquarion.libs.libtts.kokoro._backend.KPipeline")
    backend = KokoroBackend(KokoroSettings(voice_path=expected))
    backend.start()
    assert mock_kpipeline.return_value.load_voice.call_count == 1  # type:ignore[misc]
    assert mock_kpipeline.return_value.load_voice.call_args.args[0] == str(expected)  # type:ignore[misc]


def test_kokorobackend_should_log_its_initialization(logot: Logot) -> None:
    KokoroBackend(KokoroSettings())
    logot.assert_logged(logged.debug("Kokoro TTS Backend initialized."))


def test_kokorobackend_update_settings_should_log_its_action(logot: Logot) -> None:
    backend = KokoroBackend(KokoroSettings())
    backend.update_settings(KokoroSettings())
    logot.assert_logged(logged.debug("Kokoro TTS backend settings updated."))


def test_kokorobackend_convert_should_log_its_action(logot: Logot) -> None:
    text = "some text"
    backend = KokoroBackend(KokoroSettings())
    backend.start()
    list(backend.convert(text))
    logot.assert_logged(logged.debug(f"Kokoro TTS backend converting text: {text}"))


def test_kokorobackend_convert_should_truncate_long_text_in_log(logot: Logot) -> None:
    long_text = "123456789_" * 20  # len(str) == 10, 10 * 20 == 200, 200 > max log len
    expected = f"{long_text[:_TEXT_IN_LOG_MAX_LEN]}..."
    backend = KokoroBackend(KokoroSettings())
    backend.start()
    list(backend.convert(long_text))
    logot.assert_logged(logged.debug(f"Kokoro TTS backend converting text: {expected}"))


def test_kokorobackend_start_should_log_its_actions(logot: Logot) -> None:
    settings = KokoroSettings()
    backend = KokoroBackend(settings)
    backend.start()
    logot.assert_logged(
        logged.debug("Starting Kokoro TTS backend...")
        >> logged.debug("Kokoro TTS model loaded.")
        >> logged.debug(f"Kokoro TTS voice loaded: {settings.voice}")
        >> logged.debug("Kokoro TTS backend started.")
    )


def test_kokorobackend_stop_should_log_its_action(logot: Logot) -> None:
    backend = KokoroBackend(KokoroSettings())
    backend.start()
    backend.stop()
    logot.assert_logged(logged.debug("Kokoro TTS backend stopped."))


## ITTSBackend Protocol Conformity ##


def test_kokorobackend_should_conform_to_the_ittsbackend_protocol() -> None:
    backend = KokoroBackend(KokoroSettings())
    _: ITTSBackend = backend  # Typecheck protocol conformity
    assert isinstance(backend, ITTSBackend)  # Runtime check as well


def test_kokorobackend_should_be_stopped_by_default() -> None:
    backend = KokoroBackend(KokoroSettings())
    assert not backend.is_started


## .get_settings tests


def test_kokorobackend_get_settings_should_return_an_ittssettings() -> None:
    backend = KokoroBackend(KokoroSettings())
    settings = backend.get_settings()
    _: ITTSSettings = settings  # Typecheck protocol conformity
    assert isinstance(settings, ITTSSettings)  # Runtime check as well


## .update_settings tests


def test_kokorobackend_update_settings_should_accept_a_settings_argument() -> None:
    backend = KokoroBackend(KokoroSettings())
    backend.update_settings(KokoroSettings())


def test_kokorobackend_update_settings_should_require_the_settings_argument() -> None:
    backend = KokoroBackend(KokoroSettings())
    with pytest.raises(TypeError, match=r"missing .* required positional argument"):
        backend.update_settings()  # type:ignore[call-arg]


def test_kokorobackend_update_settings_should_not_return_anything() -> None:
    # CQS principle: Commands should not return anything.
    backend = KokoroBackend(KokoroSettings())
    result: None = backend.update_settings(KokoroSettings())  # type:ignore[func-returns-value]
    assert result is None


def test_kokorobackend_update_settings_should_update_settings_when_not_started() -> (
    None
):
    backend = KokoroBackend(KokoroSettings())
    orig_settings = backend.get_settings()
    new_settings = KokoroSettings(locale="en-GB", voice=KokoroVoices.bf_emma)
    backend.stop()  # Default is stopped, this is just to make sure.
    backend.update_settings(new_settings)
    updated_settings = backend.get_settings()
    assert updated_settings == new_settings
    assert updated_settings != orig_settings


def test_kokorobackend_update_settings_should_update_settings_when_already_started(
    # This is here to force Ruff to wrap line.
) -> None:
    backend = KokoroBackend(KokoroSettings())
    orig_settings = backend.get_settings()
    new_settings = KokoroSettings(locale="en-GB", voice=KokoroVoices.bf_emma)
    backend.start()
    backend.update_settings(new_settings)
    updated_settings = backend.get_settings()
    assert updated_settings == new_settings
    assert updated_settings != orig_settings


def test_kokorobackend_update_settings_should_raise_error_if_incorrect_kind() -> None:
    backend = KokoroBackend(KokoroSettings())
    incorrect_settings = AnotherTTSSettings()
    with pytest.raises(TypeError, match="Incorrect settings type"):
        backend.update_settings(incorrect_settings)


## .audio_spec tests


def test_kokorobackend_should_have_an_audio_spec_property() -> None:
    backend = KokoroBackend(KokoroSettings())
    assert hasattr(backend, "audio_spec")


def test_kokorobackend_audio_spec_should_return_a_ttsaudiospec_instance() -> None:
    backend = KokoroBackend(KokoroSettings())
    assert isinstance(backend.audio_spec, TTSAudioSpec)


def test_kokorobackend_audio_spec_should_indicate_audio_l16_format() -> None:
    backend = KokoroBackend(KokoroSettings())
    assert str(backend.audio_spec) == EXPECTED_AUDIO_SPEC


## .convert() tests


def test_kokorobackend_convert_should_require_some_text_input() -> None:
    backend = KokoroBackend(KokoroSettings())
    with pytest.raises(TypeError, match=r"missing .* required positional argument"):
        backend.convert()  # type:ignore[call-arg]


def test_kokorobackend_convert_should_return_a_generator_of_chunks_of_audio_bytes() -> (
    None
):
    backend = KokoroBackend(KokoroSettings())
    backend.start()
    audio_bytes = b"".join(list(backend.convert("some text")))
    assert len(audio_bytes) > 0
    if environ.get("KOKORO_TEST_SKIP_MOCK", "0") == "1":
        # Cannot guarantee exact same output every time when really running Kokoro.
        return  # pragma: no cover
    assert audio_bytes == b"\x00\x00\x00\x00"


def test_kokorobackend_convert_should_raise_an_error_if_backend_not_started() -> None:
    backend = KokoroBackend(KokoroSettings())
    with pytest.raises(RuntimeError, match="Backend is not started"):
        list(backend.convert("some text"))


## .is_started tests


def test_kokorobackend_is_started_should_return_true_if_started() -> None:
    backend = KokoroBackend(KokoroSettings())
    backend.start()
    assert backend.is_started


def test_kokorobackend_is_started_should_return_false_if_stopped() -> None:
    backend = KokoroBackend(KokoroSettings())
    backend.start()
    backend.stop()
    assert not backend.is_started


def test_kokorobackend_is_started_should_be_read_only() -> None:
    backend = KokoroBackend(KokoroSettings())
    with pytest.raises(AttributeError, match=r"property .* of .* object has no setter"):
        backend.is_started = True  # type:ignore[misc]


## .start() tests


def test_kokorobackend_start_should_start_the_backend() -> None:
    backend = KokoroBackend(KokoroSettings())
    backend.start()
    assert backend.is_started


def test_kokorobackend_start_should_be_idempotent() -> None:
    backend = KokoroBackend(KokoroSettings())
    backend.start()
    assert backend.is_started
    backend.start()
    assert backend.is_started


def test_kokorobackend_start_should_not_return_anything() -> None:
    # CQS principle: Commands should not return anything.
    backend = KokoroBackend(KokoroSettings())
    result: None = backend.start()  # type:ignore[func-returns-value]
    assert result is None


## .stop() tests


def test_kokorobackend_stop_should_stop_the_backend() -> None:
    backend = KokoroBackend(KokoroSettings())
    backend.start()
    assert backend.is_started
    backend.stop()
    assert not backend.is_started


def test_kokorobackend_stop_should_be_idempotent() -> None:
    backend = KokoroBackend(KokoroSettings())
    backend.start()
    assert backend.is_started
    backend.stop()
    assert not backend.is_started
    backend.stop()  # type:ignore[unreachable]  # The type checker is wrong.  Tested.
    assert not backend.is_started


def test_kokorobackend_stop_should_not_return_anything() -> None:
    # CQS principle: Commands should not return anything.
    backend = KokoroBackend(KokoroSettings())
    result: None = backend.stop()  # type:ignore[func-returns-value]
    assert result is None
