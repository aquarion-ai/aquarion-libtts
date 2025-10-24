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

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from kokoro import KModel, KPipeline
from loguru import logger

from aquarion.libs.libtts.api import ITTSSettings, TTSAudioSpec
from aquarion.libs.libtts.api._ttsbackend import TTSSampleByteOrders, TTSSampleTypes
from aquarion.libs.libtts.kokoro.settings import KokoroSettings

if TYPE_CHECKING:
    from collections.abc import Iterator

    from numpy import float32, int16
    from numpy.typing import NDArray


_TEXT_IN_LOG_MAX_LEN: Final = 100


class KokoroBackend:
    """Kokoro TTS backend."""

    def __init__(self, settings: ITTSSettings) -> None:
        """Initialize the Kokoro TTS backend with given settings."""
        if not isinstance(settings, KokoroSettings):
            message = f"Incorrect settings type: [{type(settings)}]"
            raise TypeError(message)
        self._settings = settings
        self._pipeline: KPipeline | None = None
        logger.debug("Kokoro TTS Backend initialized.")

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
        return TTSAudioSpec(
            format="Linear PCM",
            sample_rate=24000,
            sample_type=TTSSampleTypes.SIGNED_INT,
            sample_width=16,
            byte_order=TTSSampleByteOrders.LITTLE_ENDIAN,
            num_channels=1,
        )

    @property
    def is_started(self) -> bool:
        """Whether or not the backend already started.

        Returns:
            [True][] if the backend is started, [False][] otherwise.

        Note:
            This should be a read-only property.

        """
        return self._pipeline is not None

    def get_settings(self) -> KokoroSettings:
        """Return the current setting in use.

        Returns:
            The current settings in use.

        Note:
            The reason the settings are not just direct attributes is because they are
            to be treated as an all-or-nothing collection.  I.e. individual settings
            attributes should not be individually modified directly on an
            [ITTSSettingsHolder][aquarion.libs.libtts.api.ITTSSettingsHolder], but
            rather the whole settings object should be replaced with a new one.

        """
        return self._settings

    def update_settings(self, new_settings: ITTSSettings) -> None:
        """Update to the new given settings.

        Args:
            new_settings: The new complete set of settings to start using immediately.

        Raises:
            TypeError: Implementations of this interface should check that they are only
                getting the correct concrete settings class and raise an exception if
                any other kind of [ITTSSettings][aquarion.libs.libtts.api.ITTSSettings]
                is given.

        Note:
            The reason the settings are not just direct attributes is because they are
            to be treated as an all-or-nothing collection.  I.e. individual settings
            attributes should not be individually modified directly on an
            [ITTSSettingsHolder][aquarion.libs.libtts.api.ITTSSettingsHolder], but
            rather the whole settings object should be replaced with a new one.

        """
        if not isinstance(new_settings, KokoroSettings):
            message = f"Incorrect settings type: [{type(new_settings)}]"
            raise TypeError(message)
        started_state = self.is_started
        if started_state:
            self.stop()
        self._settings = new_settings
        if started_state:
            self.start()
        logger.debug("Kokoro TTS backend settings updated.")

    def convert(self, text: str) -> Iterator[bytes]:
        """Return speech audio for the given text as one or more binary chunks.

        Args:
            text: The text to convert in to speech.

        Returns:
            An [Iterator][collections.abc.Iterator] of chunks of audio in the format
                specified by
                [audio_spec][aquarion.libs.libtts.api.ITTSBackend.audio_spec].

        """
        if not self.is_started:
            message = "Backend is not started"
            raise RuntimeError(message)
        # Type narrowing for the type checker.
        assert isinstance(self._pipeline, KPipeline)  # noqa: S101
        log_text = (
            text
            if len(text) < _TEXT_IN_LOG_MAX_LEN
            else f"{text[:_TEXT_IN_LOG_MAX_LEN]}..."
        )
        logger.debug("Kokoro TTS backend converting text: {}", log_text)
        for result in self._pipeline(text, self._settings.voice, self._settings.speed):
            if result.audio is None:
                continue
            audio_array: NDArray[float32] = result.audio.numpy()
            audio_int_array: NDArray[int16] = (audio_array * 32767).astype("int16")
            yield audio_int_array.tobytes()

    def start(self) -> None:
        """Start the TTS backend.

        Note:
            If the backend is already started, this method should be idempotent and do
            nothing.

        """
        if self.is_started:
            return
        logger.debug("Starting Kokoro TTS backend...")
        model: KModel | bool = True
        if (
            self._settings.model_path is not None
            or self._settings.config_path is not None
        ):
            model = (
                KModel(
                    repo_id=self._settings.repo_id,
                    config=self._settings.config_path,
                    model=self._settings.model_path,
                )
                .to(self._settings.device)
                .eval()
            )
        self._pipeline = KPipeline(
            repo_id=self._settings.repo_id,
            lang_code=self._settings.lang_code,
            device=self._settings.device,
            model=model,
        )
        logger.debug("Kokoro TTS model loaded.")
        voice = (
            self._settings.voice
            if self._settings.voice_path is None
            else self._settings.voice_path
        )
        self._pipeline.load_voice(str(voice))
        logger.debug(f"Kokoro TTS voice loaded: {voice}")
        logger.debug("Kokoro TTS backend started.")

    def stop(self) -> None:
        """Stop the TTS backend.

        Note:
            If the backend is already started, this method should be idempotent and do
            nothing.

        """
        self._pipeline = None
        logger.debug("Kokoro TTS backend stopped.")
