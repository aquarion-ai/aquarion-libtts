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


"""Kokoro TTS settings implementation."""

from __future__ import annotations

from enum import StrEnum, auto
from types import MappingProxyType
from typing import Self, cast

from babel import Locale, UnknownLocaleError
from kokoro.pipeline import ALIASES
from loguru import logger
from pydantic import (
    ConfigDict,
    Field,
    FilePath,
    TypeAdapter,
    field_validator,
    model_validator,
)
from pydantic.dataclasses import dataclass

from aquarion.libs.libtts._utils import fake_gettext as _
from aquarion.libs.libtts.api import (
    JSONSerializableTypes,
    TTSSettingsSpecEntry,
    TTSSettingsSpecEntryTypes,
    TTSSettingsSpecType,
)


class KokoroLocales(StrEnum):
    """Voice locales supported by this backend.

    The locales also have to be supported by Kokoro in some way too, of course.
    """

    # NOTE: Cannot use auto() here since that makes all values lower case.

    #: American English (works with voices prefixed with ``af_`` or ``am_``)
    en_US = "en_US"  # noqa: N815
    #: British English (works with voices prefixed with ``bf_`` or ``bm_``)
    en_GB = "en_GB"  # noqa: N815
    #: French (works with voices prefixed with ``ff_``` or ``fm_``)
    fr_FR = "fr_FR"  # noqa: N815


class KokoroVoices(StrEnum):
    """Kokoro TTS voices supported by this backend.

    Voice grades and details can be found on
    `VOICES.md <https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md>`__

    """

    #: American female voice, grade A quality.
    af_heart = auto()
    #: American female voice, grade A- quality.
    af_bella = auto()
    #: American female voice, grade B- quality.
    af_nicole = auto()
    #: American male voice, grade C+ quality.
    am_fenrir = auto()
    #: American male voice, grade C+ quality.
    am_michael = auto()
    #: American male voice, grade C+ quality.
    am_puck = auto()
    #: British female voice, grade B- quality.
    bf_emma = auto()
    #: British male voice, grade C quality.
    bm_fable = auto()
    #: British male voice, grade C quality.
    bm_george = auto()
    #: French female voice, grade B- quality.
    ff_siwis = auto()


class KokoroDeviceNames(StrEnum):
    """Kokoro TTS device names supported by this backend.

    I.e. PyTorch device names.

    """

    cpu = auto()
    cuda = auto()


def _enum_strs(enum: type[StrEnum]) -> frozenset[str]:
    """Return a frozen set of enumeration strings."""
    return frozenset(str(entry) for entry in enum)


@dataclass(
    # NOTE: We have to use the frozen parameter in ConfigDict, not the frozen parameter
    #       for dataclass() here.  They each "freeze" in a different way and the
    #       dataclass() way breaks mypy type equivalency with ITTSSettings.
    config=ConfigDict(
        revalidate_instances="always",
        extra="forbid",
        validate_default=True,
        frozen=True,
    ),
    kw_only=True,
    slots=True,
)
class KokoroSettings:
    """Kokoro TTS backend settings.

    Note:
        To work in an offline or air-gapped environment, you must provides local paths
        for :attr:`model_path`, :attr:`config_path` and :attr:`voice_path`.

    """

    #: Used to help specify which language to speak.
    #:
    #: ``locale`` influences pronunciation, inflections, etc. of the specified voice and
    #: must be one of the locales supported by this backend.
    #:
    #: While ``locale`` must be a string to conform with the
    #: :class:`~aquarion.libs.libtts.api.ITTSSettings` interface, the valid / supported
    #: options for it are defined in :class:`KokoroLocales`.
    #:
    #: :default: :attr:`KokoroLocales.en_US`
    #:
    locale: str = "en_US"
    _locale_spec = TTSSettingsSpecEntry(
        type=str, min=2, values=_enum_strs(KokoroLocales)
    )
    _locale_display_name = _("Locale")
    _locale_description = _("The regional or international locale setting.")

    #: The voice in which to speak.
    #:
    #: Voices are either male or female and are optimized for specific languages /
    #: dialects.  ``voice`` must be selected from :class:`KokoroVoices`.
    #:
    #: For best results, use a voice that is optimized for the specified :attr:`locale`.
    #:
    #: :default: :attr:`KokoroVoices.af_heart`
    #:
    voice: KokoroVoices = KokoroVoices.af_heart
    _voice_spec = TTSSettingsSpecEntry(type=str, values=_enum_strs(KokoroVoices))
    _voice_display_name = _("Voice")
    _voice_description = _("The voice used by the text-to-speech system.")

    #: The speed at which to speak.
    #:
    #: Speech can be sped up or slowed down with this setting.
    #:
    #: ``speed`` is must be between ``0.1`` and ``2.0``, inclusive.
    #:
    #: :default: ``1.0``, i.e. normal speed.
    #:
    speed: float = Field(default=1.0, ge=0.1, le=2.0)
    _speed_spec = TTSSettingsSpecEntry(type=float, min=0.1, max=2.0)
    _speed_display_name = _("Speed")
    _speed_description = _("The speaking speed of the text-to-speech system.")

    #: The compute device to use to generate the speech.
    #:
    #: I.e. to use the GPU or only the CPU.
    #:
    #: ``device`` must be selected from :class:`KokoroDeviceNames` or be :obj:`None`.
    #: If it set to :obj:`None`, then a GPU will be used if present, with the CPU as the
    #: fallback option.
    #:
    #: :default: :obj:`None`
    #:
    #: Note:
    #:     Kokoro TTS does not currently support integer GPU numbers, so if you
    #:     you multiple GPUs, you will have to specify which one to use in some other
    #:     way. (E.g. environment variables, etc.)
    #:
    device: KokoroDeviceNames | None = None
    _device_spec = TTSSettingsSpecEntry(type=str, values=_enum_strs(KokoroDeviceNames))
    _device_display_name = _("Compute Device")
    _device_description = _(
        "The device used for running the TTS system (e.g., cpu or cuda)."
    )

    #: The `HuggingFace`_ repository ID to use to download the Kokoro Model.
    #:
    #: This normally does not need to be changed, unless you have an alternative
    #: download location that works with the HuggingFace API.
    #:
    #: :default: ``hexgrad/Kokoro-82M``
    #:
    #: .. _HuggingFace: https://huggingface.co/hexgrad/Kokoro-82M
    #:
    repo_id: str = "hexgrad/Kokoro-82M"
    _repo_id_spec = TTSSettingsSpecEntry(type=str)
    _repo_id_display_name = _("Repository ID")
    _repo_id_description = _(
        "The identifier or path of the Kokoro TTS HuggingFace repository."
    )

    #: Offline mode local file path to the Kokoro TTS model file.
    #:
    #: This is only required for offline or air-gapped use; otherwise, files are
    #: downloaded and cached automatically.
    #:
    #: :default: :obj:`None`
    #:
    #: Example:
    #:     ``~/my_kokoro_tts_downloads/kokoro-v1_0.pth``
    #:
    model_path: FilePath | None = None
    _model_path_spec = TTSSettingsSpecEntry(type=str)
    _model_path_display_name = _("Model File Path")
    _model_path_description = _(
        "The file path to the Kokoro TTS model file.  Required only for offline or "
        "air-gapped use; otherwise, files are downloaded and cached automatically."
    )

    #: Offline mode local file path to the Kokoro TTS config file.
    #:
    #: This is only required for offline or air-gapped use; otherwise, files are
    #: downloaded and cached automatically.
    #:
    #: :default: :obj:`None`
    #:
    #: Example:
    #:     ``~/my_kokoro_tts_downloads/config.json``
    #:
    config_path: FilePath | None = None
    _config_path_spec = TTSSettingsSpecEntry(type=str)
    _config_path_display_name = _("Configuration File Path")
    _config_path_description = _(
        "The file path to the Kokoro TTS configuration file.  Required only for offline"
        " or air-gapped use; otherwise, files are downloaded and cached automatically."
    )

    #: Offline mode local file path to the Kokoro TTS voice file.
    #:
    #: This is only required for offline or air-gapped use; otherwise, files are
    #: downloaded and cached automatically.
    #:
    #: If ``voice_path`` is not :obj:`None`, then the :attr:`voice`` attribute is
    #: ignored.
    #:
    #: :default: :obj:`None`
    #:
    #: Example:
    #:     ``~/my_kokoro_tts_downloads/voices/af_heart.pt``
    #:
    voice_path: FilePath | None = None
    _voice_path_spec = TTSSettingsSpecEntry(type=str)
    _voice_path_display_name = _("Voice File Path")
    _voice_path_description = _(
        "The file path to the Kokoro TTS voice file.  Required only for offline or "
        "air-gapped use; otherwise, files are downloaded and cached automatically."
    )

    @property
    def lang_code(self) -> str:
        """The Kokoro TTS language code for the current locale.

        E.g. ``a`` for American English, ``b`` for British English, ``f`` for French,
        etc.

        This is not a settings, it is a derived property used by the Kokoro backend.

        """
        return ALIASES[self.locale.lower().replace("_", "-")]

    def to_dict(self) -> dict[str, JSONSerializableTypes]:
        """Export all settings as a dictionary of only JSON-serializable types.

        Returns:
            A dictionary where the keys are the setting names and the values are the
            setting values converted as necessary to simple base JSON-compatible types.

        Example:
            .. code:: JSON

                {
                    "locale": "en_US",
                    "voice": "af_heart",
                    "speed": 1.0,
                    "device": "cuda",
                    "repo_id": "hexgrad/Kokoro-82M",
                    "model_path": "kokoro-v1_0.pth",
                    "config_path": "config.json",
                    "voice_path": "af_heart.pt",
                }

        """
        settings_dict = cast(
            "dict[str, JSONSerializableTypes]",
            TypeAdapter(self.__class__).dump_python(self, mode="json"),
        )
        logger.debug(f"KokoroSettings dictionary created: {settings_dict!s}")
        return settings_dict

    @field_validator("locale", mode="before")
    @classmethod
    def _validate_locale(cls, locale: str) -> str:
        """Validate the locale value."""
        separator = "_" if "_" in locale else "-"
        try:
            valid_locale = Locale.parse(locale, sep=separator)
        except (ValueError, UnknownLocaleError, TypeError) as e:
            message = f"Invalid locale: {locale}"
            raise ValueError(message) from e
        # Locale will strip out variants and modifiers automatically, so we do not need
        # to handle those.
        valid_locale.script = None  # Kokoro does not support scripts either.
        try:
            supported_locale = KokoroLocales[str(valid_locale)]
        except KeyError as e:
            message = f"Unsupported locale: {locale}"
            raise ValueError(message) from e
        return str(supported_locale)

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

    @classmethod
    def _make_spec(
        cls,
    ) -> TTSSettingsSpecType:
        """Return a specification that describes all the backend's settings.

        This must conform to ITTSPlugin.get_settings_spec(), even though it is
        implemented here.

        This way all Pydantic-specific code is kept together.
        """
        spec: dict[str, TTSSettingsSpecEntry[TTSSettingsSpecEntryTypes]] = {}
        for setting in cls.__dataclass_fields__:  # type:ignore[misc]
            spec[setting] = cast(
                "TTSSettingsSpecEntry[TTSSettingsSpecEntryTypes]",
                getattr(cls, f"_{setting}_spec"),
            )
        # MappingProxyType makes the dict read-only.
        return MappingProxyType(spec)

    @classmethod
    def _get_setting_display_name(cls, setting_name: str) -> str:
        """Return the default display name for the given setting."""
        return cast("str", getattr(cls, f"_{setting_name}_display_name"))

    @classmethod
    def _get_setting_description(cls, setting_name: str) -> str:
        """Return the default description for the given setting."""
        return cast("str", getattr(cls, f"_{setting_name}_description"))
