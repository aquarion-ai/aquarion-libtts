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

from enum import StrEnum, auto
from typing import Annotated, Final, Self, cast

from babel import Locale, UnknownLocaleError
from kokoro.pipeline import ALIASES
from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    FilePath,
    model_validator,
)

from aquarion.libs.libtts.api import JSONSerializableTypes

_VOICE_LOCALE_ALIASES: Final = {
    "en_CA": "en_US",
    "fr_CA": "fr_FR",
}


class KokoroLocales(StrEnum):
    """Voice locales supported by this backend.

    The locales also have to be supported by Kokoro in some way too, of course.
    """

    # NOTE: Cannot use auto() here since that makes all values lower case.

    en_CA = "en_CA"  # noqa: N815
    en_US = "en_US"  # noqa: N815
    en_GB = "en_GB"  # noqa: N815
    fr_CA = "fr_CA"  # noqa: N815
    fr_FR = "fr_FR"  # noqa: N815


class KokoroVoices(StrEnum):
    """Kokoro TTS voices supported by this backend."""

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


class KokoroDeviceNames(StrEnum):
    """Kokoro TTS device names supported by this backend.

    I.e. PyTorch device names.
    """

    cpu = auto()
    cuda = auto()


def _validate_locale(locale: str) -> str:
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


class KokoroSettings(  # type:ignore[explicit-any]
    BaseModel, revalidate_instances="always", extra="forbid", validate_default=True
):
    """Kokoro TTS backend settings.

    `locale` must be one of the locales supported by this backend.  Namely:

      - en_CA (Alias for en_US)
      - en_US
      - en_GB
      - fr_CA (Alias for fr_FR)
      - fr_FR

      Of course, it will be also supported by Kokoro TTS in some way or other as well.

    `voice` must be one from KokoroVoices.

    `speed` is must be between 0.1 and 1.0.

    `device` does not support integer GPU numbers.  The only valid values are in
    `KokoroDeviceNames`.

    If `voice_path` is not `None`, then the voice attribute is ignored.

    To work in an offline or air-gapped environment, you must provides local paths for
    `model_path`, `config_path` and `voice_path`.

    """

    locale: Annotated[str, BeforeValidator(_validate_locale)] = "en_CA"
    voice: KokoroVoices = KokoroVoices.af_heart
    speed: Annotated[float, Field(gt=0, le=1.0)] = 1.0
    device: KokoroDeviceNames | None = None
    repo_id: str = "hexgrad/Kokoro-82M"
    model_path: FilePath | None = None
    config_path: FilePath | None = None
    voice_path: FilePath | None = None

    @property
    def lang_code(self) -> str:
        """Return the language code for the current locale."""
        voice_locale = (
            _VOICE_LOCALE_ALIASES.get(self.locale, self.locale)
            .lower()
            .replace("_", "-")
        )
        return ALIASES[voice_locale]

    def to_dict(self) -> dict[str, JSONSerializableTypes]:
        """Export all settings as a dictionary of only built-in Python types."""
        return cast("dict[str, JSONSerializableTypes]", self.model_dump(mode="json"))

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
