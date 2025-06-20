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

"""Unit tests for the _utils module."""

from gettext import NullTranslations

import pytest

from aquarion.libs.libtts._utils import load_internal_language

### load_internal_language Tests ###


def test_load_internal_language_should_accept_a_locale_argument() -> None:
    load_internal_language(locale="en_CA")


def test_load_internal_language_should_require_the_locale_argument() -> None:
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        load_internal_language()


def test_load_internal_language_should_return_gettext_and_translations_instance() -> (
    None
):
    _, t = load_internal_language("en_CA")
    assert hasattr(_, "__func__")
    # Had to do it this way because id(t.gettext) != id(t.gettext). O_o
    assert _.__func__.__name__ == "gettext"  # type:ignore[misc]
    assert isinstance(t, NullTranslations)


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("en_CA", "I am translated in to en_CA"),
    ],
)
def test_load_internal_language_should_load_the_correct_translation_catalog(
    locale: str, expected: str
) -> None:
    _, t = load_internal_language(locale)
    translated: str = _("I am not translated")
    assert translated == expected
