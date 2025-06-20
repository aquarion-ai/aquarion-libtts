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


"""Utility functions for aquarion-libtts."""

from functools import partial
from importlib.resources import files
from typing import Final, cast

from aquarion.libs.libtts.__about__ import __name__ as project_name
from aquarion.libs.libtts.api import HashableTraversable, load_language

LOCALE_PATH: Final[HashableTraversable] = cast(
    "HashableTraversable", files(__name__) / "locale"
)


load_internal_language = partial(
    load_language, domain=project_name, locale_path=LOCALE_PATH
)


def _language_test_string() -> None:  # pragma: no cover
    """Container for a test string to translate. Do not call."""

    def _(string: str) -> str:
        return string

    # Translator: This should be translated to say "I am translated in to {locale}".
    # E.g. "I am translated in to en_CA". It is only used for testing.
    _("I am not translated")
