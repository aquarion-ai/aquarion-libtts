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

"""Unit tests for _kokoro module."""

from os import environ
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, TypedDict, cast

import pytest
import torch
from kokoro.pipeline import KPipeline
from pytest_mock import MockerFixture

from aquarion.libs.libtts._kokoro import (
    KokoroBackend,
    KokoroDeviceNames,
    KokoroPlugin,
    KokoroSettings,
    KokoroVoices,
)
from aquarion.libs.libtts.api import (
    ITTSBackend,
    ITTSPlugin,
    ITTSSettings,
    JSONSerializableTypes,
    TTSSpeechData,
)
from tests.api.ttssettings_test import AnotherTTSSettings

if TYPE_CHECKING:
    from collections.abc import Mapping

### KokoroSettings Tests ###


class SettingsDict(TypedDict, total=False):
    """Types for KokoroSettings dicts and arguments."""

    locale: str
    voice: KokoroVoices
    speed: float
    device: str | None
    repo_id: str
    model_path: Path | None
    config_path: Path | None
    voice_path: Path


SETTINGS_ARGS: Final[SettingsDict] = {
    "locale": "en-GB",
    "voice": KokoroVoices.bf_emma,
    "speed": 0.8,
    "device": "cuda",
    "repo_id": "hexgrad/Kokoro-82M",
    "model_path": Path("kokoro-v1_0.pth"),
    "config_path": Path("config.json"),
    "voice_path": Path("af_heart.pt"),
}
SETTINGS_ATTRS: Final = [*list(SETTINGS_ARGS), "lang_code"]
INVALID_SETTINGS_CASES: Final = [
    ("locale", "xx-XX", "Invalid locale"),
    ("locale", "en-CA", "Unsupported locale"),
    ("voice", "xf_not_exist", "Input should be 'af_heart'"),
    ("voice", KokoroVoices.ff_siwis, "Invalid voice for the locale: en-US"),
    ("speed", -1, "greater than 0"),
    ("speed", 0, "greater than 0"),
    ("speed", 1.1, "less than or equal to 1"),
    ("device", "bad_device", "Input should be 'cpu'"),
    ("model_path", Path("bad/exist"), "Path does not point to a file"),
    ("config_path", Path("bad/exist"), "Path does not point to a file"),
    ("voice_path", Path("bad/exist"), "Path does not point to a file"),
]


@pytest.fixture(scope="session")
def real_settings_path_args(
    tmp_path_factory: pytest.TempPathFactory,
) -> SettingsDict:
    tmp_dir_path = tmp_path_factory.mktemp("kokoro_data")
    path_args = {}
    for argument, file_name in SETTINGS_ARGS.items():
        if not argument.endswith("_path"):
            continue
        file_path = tmp_dir_path / cast("str", file_name)
        file_path.touch()
        path_args[argument] = file_path
    return cast("SettingsDict", path_args)


def test_kokorosettings_should_accept_attributes_as_kwargs(
    real_settings_path_args: SettingsDict,
) -> None:
    arguments = SETTINGS_ARGS.copy()
    arguments.update(real_settings_path_args)
    KokoroSettings(**arguments)  # type:ignore[arg-type]


def test_kokorosettings_should_only_accept_keyword_arguments(
    real_settings_path_args: SettingsDict,
) -> None:
    arguments = SETTINGS_ARGS.copy()
    arguments.update(real_settings_path_args)
    with pytest.raises(
        TypeError, match="takes 1 positional argument but .* were given"
    ):
        KokoroSettings(*arguments.values())


@pytest.mark.parametrize("attribute", SETTINGS_ARGS)
def test_kokorosettings_should_store_given_settings_values(
    real_settings_path_args: SettingsDict, attribute: str
) -> None:
    arguments = SETTINGS_ARGS.copy()
    arguments.update(real_settings_path_args)
    settings = KokoroSettings(**arguments)  # type:ignore[arg-type]
    assert getattr(settings, attribute) == arguments.get(attribute)  # type:ignore[misc]


@pytest.mark.parametrize(("attr", "value", "err_msg"), INVALID_SETTINGS_CASES)  # type:ignore[misc]
def test_kokorosettings_should_raise_an_exception_if_a_setting_is_invalid(  # type:ignore[explicit-any,misc]
    attr: str,
    value: Any,  # noqa: ANN401
    err_msg: str,
) -> None:
    with pytest.raises(ValueError, match=err_msg):
        KokoroSettings(**{attr: value})  # type:ignore[misc]


@pytest.mark.parametrize(("attr"), SETTINGS_ATTRS)
def test_kokorosettings_should_have_expected_attributes(attr: str) -> None:
    settings = KokoroSettings()
    assert hasattr(settings, attr)


def test_kokorosettings_should_not_allow_extra_arguments() -> None:
    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        KokoroSettings(extra_argument="value")  # type: ignore[call-arg]


def test_kokorosettings_should_not_allow_extra_attributes() -> None:
    settings = KokoroSettings()
    with pytest.raises(ValueError, match='object has no field "extra_attribute"'):
        settings.extra_attribute = "value"  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("locale", "voice", "expected"),
    [
        ("en-US", KokoroVoices.af_heart, "a"),
        ("en-GB", KokoroVoices.bf_emma, "b"),
        ("fr-FR", KokoroVoices.ff_siwis, "f"),
    ],
)
def test_kokorosettings_lang_code_should_return_the_correct_language_code(
    locale: str, voice: KokoroVoices, expected: str
) -> None:
    settings = KokoroSettings(locale=locale, voice=voice)
    assert settings.lang_code == expected


def test_kokorosettings_to_dict_should_return_voice_as_a_string() -> None:
    settings = KokoroSettings(voice=KokoroVoices.af_heart)
    settings_dict: dict[str, str | float] = settings.to_dict()
    assert isinstance(settings_dict["voice"], str)
    assert settings_dict["voice"] == "af_heart"


def test_kokorosettings_to_dict_should_return_device_as_a_string() -> None:
    settings = KokoroSettings(device=KokoroDeviceNames.cuda)
    settings_dict: dict[str, str | float] = settings.to_dict()
    assert isinstance(settings_dict["device"], str)
    assert settings_dict["device"] == "cuda"


def test_kokorosettings_should_coerce_voice_strings_to_enum_on_instantiation() -> None:
    settings = KokoroSettings(voice="af_heart")  # type: ignore[arg-type]
    assert settings.voice == KokoroVoices.af_heart
    assert isinstance(settings.voice, KokoroVoices)


def test_kokorosettings_should_coerce_device_strings_to_enum_on_instantiation() -> None:
    settings = KokoroSettings(device="cpu")  # type: ignore[arg-type]
    assert settings.device == KokoroDeviceNames.cpu
    assert isinstance(settings.device, KokoroDeviceNames)


@pytest.mark.parametrize(
    "attribute", [attr for attr in SETTINGS_ARGS if attr.endswith("_path")]
)
def test_kokorosettings_should_raise_an_error_if_file_path_does_not_exist(
    attribute: str,
) -> None:
    with pytest.raises(ValueError, match="Path does not point to a file"):
        KokoroSettings(**{attribute: Path("non-existant-path")})  # type:ignore[arg-type]


## ITTSSettings Protocol Conformity ##


def test_kokorosettings_should_conform_to_the_ittssettings_protocol() -> None:
    settings = KokoroSettings()
    _: ITTSSettings = settings  # Typecheck protocol conformity
    assert isinstance(settings, ITTSSettings)  # Runtime check as well


def test_kokorosettings_should_have_a_locale_attribute() -> None:
    settings: ITTSSettings = KokoroSettings()
    assert isinstance(settings.locale, str)


@pytest.mark.parametrize(
    ("attr", "value"),
    [("locale", "en-US"), ("voice", "af_heart"), ("speed", 1.0)],
)
def test_kokorosettings_to_dict_should_return_a_dict_of_all_settings_as_base_types(
    attr: str, value: str | float
) -> None:
    settings = KokoroSettings(**{attr: value})  # type: ignore[arg-type]
    settings_dict: dict[str, str | float] = settings.to_dict()
    assert settings_dict[attr] == value


def test_kokorosettings_should_equate_if_setting_values_are_equal() -> None:
    settings1 = KokoroSettings()
    settings2 = KokoroSettings()
    assert settings1 == settings2
    assert settings1 is not settings2


def test_kokorosettings_should_not_equate_if_setting_values_are_different() -> None:
    settings1 = KokoroSettings()
    settings2 = KokoroSettings(locale="en-GB", voice=KokoroVoices.bf_emma)
    assert settings1 != settings2
    assert settings1 is not settings2


### KokoroBackend Tests ###


EXPECTED_AUDIO = (
    b"RIFF(\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\xc0]\x00\x00\x80\xbb"
    b"\x00\x00\x02\x00\x10\x00data\x04\x00\x00\x00\x00\x00\x00\x00"
)


@pytest.fixture(autouse=True)
def mock_kpipeline(mocker: MockerFixture) -> None:
    # If this environment variable is set, do not mock anything.  This is only for
    # debugging tests.  Use acceptance tests to test the actual Kokoro backend.
    if environ.get("KOKORO_TEST_SKIP_MOCK", "0") == "1":  # pragma: no cover
        return
    mock_audio_result: KPipeline.Result = mocker.MagicMock(spec_set=KPipeline.Result)
    mock_audio_result.audio = cast("torch.FloatTensor", torch.zeros(1, 2))  # type: ignore [misc]
    mock_no_audio_result: KPipeline.Result = mocker.MagicMock(spec_set=KPipeline.Result)
    mock_no_audio_result.audio = None  # type: ignore [misc]
    call_return_value: list[KPipeline.Result] = [
        mock_no_audio_result,
        mock_audio_result,
    ]
    mocker.patch.object(KPipeline, "__init__", return_value=None)
    mocker.patch.object(KPipeline, "load_voice", return_value=None)
    mocker.patch.object(KPipeline, "__call__", return_value=call_return_value)


def test_kokorobackend_should_accept_a_settings_argument() -> None:
    KokoroBackend(settings=KokoroSettings())


def test_kokorobackend_should_accept_settings_as_a_positional_argument() -> None:
    KokoroBackend(KokoroSettings())


def test_kokorobackend_should_require_the_settings_argument() -> None:
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        KokoroBackend()  # type: ignore [call-arg]


def test_kokorobackend_should_require_settings_to_be_instance_of_kokorosettings() -> (
    None
):
    with pytest.raises(TypeError, match="Incorrect settings type"):
        KokoroBackend(settings=AnotherTTSSettings)  # type: ignore[arg-type]


@pytest.mark.skipif(
    environ.get("KOKORO_TEST_SKIP_MOCK", "0") == "1",
    reason="Exact audio output cannot be guaranteed",
)
def test_kokorobackend_convert_should_return_expected_speech_audio() -> None:
    backend = KokoroBackend(KokoroSettings())
    backend.start()
    speech_data = backend.convert("some text")
    assert speech_data.audio == EXPECTED_AUDIO


def test_kokorobackend_should_use_local_model_path_when_given(
    real_settings_path_args: dict[str, Path], mocker: MockerFixture
) -> None:
    expected = real_settings_path_args["model_path"]
    mock_kmodel = mocker.patch("aquarion.libs.libtts._kokoro.KModel")
    backend = KokoroBackend(KokoroSettings(model_path=expected))
    backend.start()
    assert mock_kmodel.call_count == 1
    assert mock_kmodel.call_args.kwargs["model"] == expected  # type:ignore[misc]


def test_kokorobackend_should_use_local_config_path_when_given(
    real_settings_path_args: dict[str, Path], mocker: MockerFixture
) -> None:
    expected = real_settings_path_args["config_path"]
    mock_kmodel = mocker.patch("aquarion.libs.libtts._kokoro.KModel")
    backend = KokoroBackend(KokoroSettings(config_path=expected))
    backend.start()
    assert mock_kmodel.call_count == 1
    assert mock_kmodel.call_args.kwargs["config"] == expected  # type:ignore[misc]


def test_kokorobackend_should_use_local_voice_path_when_given(
    real_settings_path_args: dict[str, Path], mocker: MockerFixture
) -> None:
    expected = real_settings_path_args["voice_path"]
    mock_kpipeline = mocker.patch("aquarion.libs.libtts._kokoro.KPipeline")
    backend = KokoroBackend(KokoroSettings(voice_path=expected))
    backend.start()
    assert mock_kpipeline.return_value.load_voice.call_count == 1  # type:ignore[misc]
    assert mock_kpipeline.return_value.load_voice.call_args.args[0] == str(expected)  # type:ignore[misc]


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
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        backend.update_settings()  # type: ignore [call-arg]


def test_kokorobackend_update_settings_should_not_return_anything() -> None:
    # CQS principle: Commands should not return anything.
    backend = KokoroBackend(KokoroSettings())
    result: None = backend.update_settings(KokoroSettings())  # type: ignore [func-returns-value]
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


## .convert() tests


def test_kokorobackend_convert_should_require_some_text_input() -> None:
    backend = KokoroBackend(KokoroSettings())
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        backend.convert()  # type: ignore [call-arg]


def test_kokorobackend_convert_should_return_a_ttsspeechdata_object() -> None:
    backend = KokoroBackend(KokoroSettings())
    backend.start()
    speech_data = backend.convert("some text")
    assert isinstance(speech_data, TTSSpeechData)


def test_ittsbackend_convert_should_raise_an_error_if_backend_not_started() -> None:
    backend = KokoroBackend(KokoroSettings())
    with pytest.raises(RuntimeError, match="Backend is not started"):
        backend.convert("some text")


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
    with pytest.raises(AttributeError, match="property .* of .* object has no setter"):
        backend.is_started = True  # type: ignore [misc]


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
    result: None = backend.start()  # type: ignore [func-returns-value]
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
    backend.stop()  # type: ignore [unreachable]  # The type checker is wrong.  Tested.
    assert not backend.is_started


def test_kokorobackend_stop_should_not_return_anything() -> None:
    # CQS principle: Commands should not return anything.
    backend = KokoroBackend(KokoroSettings())
    result: None = backend.stop()  # type: ignore [func-returns-value]
    assert result is None


### KokoroPlugin Tests ###


## ITTSPlugin Protocol Conformity ##


def test_kokoroplugin_should_conform_to_its_protocol() -> None:
    plugin = KokoroPlugin()
    _: ITTSPlugin = plugin  # Typecheck protocol conformity
    assert isinstance(plugin, ITTSPlugin)  # Runtime check as well


def test_kokoroplugin_should_have_an_id_attribute() -> None:
    plugin = KokoroPlugin()
    assert hasattr(plugin, "id")


def test_kokoroplugin_id_should_be_immutable() -> None:
    plugin = KokoroPlugin()
    with pytest.raises(AttributeError, match="object has no setter"):
        plugin.id = "new_id"  # type: ignore [misc]


def test_kokoroplugin_id_should_have_the_correct_value() -> None:
    plugin = KokoroPlugin()
    assert plugin.id == "kokoro_v1"


## .get_display_name test


def test_kokoroplugin_get_display_name_should_accept_a_locale_argument() -> None:
    plugin = KokoroPlugin()
    plugin.get_display_name("en_CA")


def test_kokoroplugin_get_display_name_should_require_the_locale_argument() -> None:
    plugin = KokoroPlugin()
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        plugin.get_display_name()  # type: ignore [call-arg]


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("en_CA", "Kokoro"),
        ("en_US", "Kokoro"),
        ("en_GB", "Kokoro"),
        ("fr_CA", "Kokoro"),
        ("fr_FR", "Kokoro"),
    ],
)
def test_kokoroplugin_get_display_name_should_return_correct_display_name_for_locale(
    locale: str, expected: str
) -> None:
    plugin = KokoroPlugin()
    display_name = plugin.get_display_name(locale)
    assert display_name == expected


def test_kokoroplugin_get_display_name_should_return_a_fallback_if_locale_unknown() -> (
    None
):
    plugin = KokoroPlugin()
    display_name = plugin.get_display_name("ja")
    assert display_name == "Kokoro"


## .make_settings tests


@pytest.mark.parametrize(("attribute"), SETTINGS_ARGS)
def test_kokoroplugin_make_settings_should_use_default_values_when_no_values_given(
    attribute: str,
) -> None:
    plugin = KokoroPlugin()
    settings = plugin.make_settings()
    assert isinstance(settings, KokoroSettings)  # For the type checker
    assert (
        getattr(settings, attribute) == KokoroSettings.model_fields[attribute].default  # type: ignore[misc]
    )


@pytest.mark.parametrize(("attribute"), SETTINGS_ARGS)
def test_kokoroplugin_make_settings_should_use_given_values_when_values_are_given(
    real_settings_path_args: SettingsDict, attribute: str
) -> None:
    settings_dict = SETTINGS_ARGS.copy()
    settings_dict.update(real_settings_path_args)
    plugin = KokoroPlugin()
    settings = plugin.make_settings(
        from_dict=cast("Mapping[str, JSONSerializableTypes]", settings_dict)
    )
    assert isinstance(settings, KokoroSettings)  # For the type checker
    assert getattr(settings, attribute) == settings_dict.get(attribute)  # type:ignore[misc]


def test_kokoroplugin_make_settings_should_return_a_ittssettings_object() -> None:
    plugin = KokoroPlugin()
    settings = plugin.make_settings()
    _: ITTSSettings = settings  # Typecheck protocol conformity
    assert isinstance(settings, ITTSSettings)  # Runtime check as well


def test_kokoroplugin_make_settings_should_raise_an_error_if_an_invalid_key_given() -> (
    None
):
    plugin = KokoroPlugin()
    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        plugin.make_settings(from_dict={"invalid": None})


@pytest.mark.parametrize(("attr", "value", "err_msg"), INVALID_SETTINGS_CASES)  # type:ignore[misc]
def test_kokoroplugin_make_settings_should_raise_an_error_if_an_invalid_value_given(  # type:ignore[explicit-any,misc]
    attr: str,
    value: Any,  # noqa: ANN401
    err_msg: str,
) -> None:
    plugin = KokoroPlugin()
    with pytest.raises(ValueError, match=err_msg):
        plugin.make_settings(from_dict={attr: value})  # type:ignore[misc]


## .make_backend tests


def test_kokoroplugin_make_backend_should_require_a_settings_argument() -> None:
    plugin = KokoroPlugin()
    with pytest.raises(TypeError, match="missing *. required positional argument"):
        plugin.make_backend()  # type: ignore [call-arg]


def test_kokoroplugin_make_backend_should_use_the_given_settings() -> None:
    plugin = KokoroPlugin()
    expected_settings = plugin.make_settings()
    backend = plugin.make_backend(expected_settings)
    settings = backend.get_settings()
    assert isinstance(settings, KokoroSettings)  # For the type checker
    assert settings == expected_settings


def test_kokoroplugin_make_backend_should_return_a_ittsbackend_object() -> None:
    plugin = KokoroPlugin()
    settings = plugin.make_settings()
    backend = plugin.make_backend(settings)
    _: ITTSBackend = backend  # Typecheck protocol conformity
    assert isinstance(backend, ITTSBackend)  # Runtime check as well


def test_kokoroplugin_make_backend_should_raise_error_if_incorrect_settings_given() -> (
    None
):
    plugin = KokoroPlugin()
    settings = AnotherTTSSettings()
    with pytest.raises(TypeError, match="Incorrect settings type"):
        plugin.make_backend(settings)
