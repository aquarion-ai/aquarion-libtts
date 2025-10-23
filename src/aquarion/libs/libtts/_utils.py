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


"""Utility functions for *aquarion-libtts*."""

from __future__ import annotations

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


def fake_gettext(string: str) -> str:
    """Fake gettext _() function that just returns the original string.

    This is useful for when i18n message definition and it's actual translation are done
    at different times.  E.g. defined at import or class definition time, but actually
    translated at runtime.

    Example usage:

    from aquarion.libs.libtts._utils import fake_gettext as _

    class_var = _("some text")


    Naming this function as _() will cause Babel to extract the text to the message
    template, but actual translation would have to be done later with something like

    return _(class_var)

    where _() in this case is the real gettext.

    """
    return string


def _language_test_string() -> None:  # pragma: no cover
    """Container for a test string to translate. Do not call."""
    _ = fake_gettext
    # Translator: This should be translated to say "I am translated in to {locale}".
    # E.g. "I am translated in to en_CA". It is only used for testing.
    _("I am not translated")
