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


"""Kokoro TTS backend implementation."""

import wave
from enum import StrEnum, auto
from io import BytesIO
from typing import TYPE_CHECKING, Annotated, Any, Self

from babel import Locale, UnknownLocaleError
from kokoro import KPipeline
from kokoro.pipeline import ALIASES
from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    model_validator,
)

from aquarion.libs.libtts.api._ttssettings import ITTSSettings
from aquarion.libs.libtts.api._ttsspeechdata import TTSSpeechData

if TYPE_CHECKING:
    from numpy import float32, int16
    from numpy.typing import NDArray


class KokoroVoices(StrEnum):
    """Supported Kokoro TTS voices."""

    # Voice grades and details can be found at:
    # https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md

    af_heart = auto()  # Grade A
    af_bella = auto()  # Grade A-
    af_nicole = auto()  # Grade B-
    am_fenrir = auto()  # Grade C+
    am_michael = auto()  # Grade C+
    am_puck = auto()  # Grade C+
    bf_emma = auto()  # Grade B-
    bm_fable = auto()  # Grade C
    bm_george = auto()  # Grade C
    ff_siwis = auto()  # Grade B-


def _validate_locale(locale: str) -> str:
    """Validate the locale value."""
    separator = "_" if "_" in locale else "-"
    try:
        loc = Locale.parse(locale, sep=separator)
    except (ValueError, UnknownLocaleError, TypeError) as e:
        message = f"Invalid locale: {locale}"
        raise ValueError(message) from e
    # Locale will strip out variants and modifiers automatically, so we do not need
    # to handle those.
    loc.script = None  # Kokoro does not support scripts either.
    locale = str(loc).replace("_", "-")  # Normalize to CLDR format.
    if locale.lower() not in ALIASES:
        message = f"Unsupported locale: {locale}"
        raise ValueError(message)
    return locale


class KokoroSettings(  # type: ignore [explicit-any, misc]
    BaseModel, revalidate_instances="always", extra="forbid", validate_default=True
):
    """Kokoro TTS backend settings."""

    locale: Annotated[str, AfterValidator(_validate_locale)] = "en-US"
    voice: KokoroVoices = KokoroVoices.af_heart
    speed: Annotated[float, Field(gt=0, le=1.0)] = 1.0

    @property
    def lang_code(self) -> str:
        """Return the language code for the current locale."""
        return ALIASES[self.locale.lower()]

    def to_dict(self) -> dict[str, Any]:  # type: ignore [explicit-any]
        """Export all settings as a dictionary of only built-in Python types."""
        return self.model_dump()  # type: ignore [misc]

    @model_validator(mode="after")
    def _validate_voice(self) -> Self:
        """Validate the voice value based on the locale."""
        if str(self.voice)[0] != self.lang_code:
            message = (
                f"Invalid voice for the locale: {self.locale}.  "
                f"Voice should start with {self.lang_code}."
            )
            raise ValueError(message)
        return self


class KokoroBackend:
    """Kokoro TTS backend."""

    def __init__(self, settings: ITTSSettings) -> None:
        """Initialize the Kokoro TTS backend with given settings."""
        if not isinstance(settings, KokoroSettings):
            message = f"Incorrect settings type: [{type(settings)}]"
            raise TypeError(message)
        self._settings = settings
        self._pipeline: KPipeline | None = None

    def get_settings(self) -> KokoroSettings:
        """Return the current settings in use.

        The reason the settings are not just a direct attribute is because they are to
        be treated as all-or-nothing collection.  I.e. individual settings attributes
        should not be individually modified directly, but rather the whole settings
        object should be replaced with a new one.
        """
        return self._settings

    def update_settings(self, new_settings: ITTSSettings) -> None:
        """Update to the new given settings."""
        if not isinstance(new_settings, KokoroSettings):
            message = f"Incorrect settings type: [{type(new_settings)}]"
            raise TypeError(message)
        started_state = self.is_started
        if started_state:
            self.stop()
        self._settings = new_settings
        if started_state:
            self.start()

    def convert(self, text: str) -> TTSSpeechData:
        """Return speech audio generated from the given text.

        The audio is in Mono WAV format with 16-bit samples and a sample rate of 24kHz.

        ATTENTION: The audio format is likely to change in the future.
        """
        if not self.is_started:
            message = "Backend is not started"
            raise RuntimeError(message)
        audio_buffer = BytesIO()
        with wave.open(audio_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono audio
            wav_file.setsampwidth(2)  # 16-bit samples
            wav_file.setframerate(24000)  # 24kHz sample rate
            assert isinstance(self._pipeline, KPipeline)  # noqa: S101
            for result in self._pipeline(
                text, self._settings.voice, self._settings.speed
            ):
                if result.audio is None:
                    continue
                audio_array: NDArray[float32] = result.audio.numpy()
                audio_int_array: NDArray[int16] = (audio_array * 32767).astype("int16")
                wav_file.writeframes(audio_int_array.tobytes())
        return TTSSpeechData(audio=audio_buffer.getvalue(), mime_type="audio/wav")

    @property
    def is_started(self) -> bool:
        """Return True if TTS backend is started / running, False otherwise.

        The reason this is a property and not just an attribute is because it should be
        read-only.
        """
        return self._pipeline is not None

    def start(self) -> None:
        """Start the TTS backend."""
        if self.is_started:
            return
        self._pipeline = KPipeline(
            repo_id="hexgrad/Kokoro-82M", lang_code=self._settings.lang_code
        )
        self._pipeline.load_voice(self._settings.voice)

    def stop(self) -> None:
        """Stop the TTS backend."""
        self._pipeline = None
