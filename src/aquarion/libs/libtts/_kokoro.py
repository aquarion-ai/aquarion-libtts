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

from enum import StrEnum, auto
from typing import Annotated, Any, Self

from babel import Locale, UnknownLocaleError
from kokoro.pipeline import ALIASES
from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    model_validator,
)


class KokoroVoices(StrEnum):
    """Kokoro TTS voices."""

    af_heart = auto()
    af_bella = auto()
    af_nicole = auto()
    bf_emma = auto()
    ff_siwis = auto()


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
