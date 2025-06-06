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


"""Unit tests for api._i18n."""

from gettext import NullTranslations
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from babel import UnknownLocaleError
from logot import Logot, logged

from aquarion.libs.libtts.api._i18n import load_language

if TYPE_CHECKING:
    from os import PathLike


### load_language Tests ###


TEST_LOCALE_PATH = files(__name__) / "locale"


def test_load_language_should_accept_all_required_arguments() -> None:
    load_language("en_CA", "some domain", "some path")


def test_load_language_should_accept_a_local_path_of_type_pathlike() -> None:
    path: PathLike[str] = Path("some path")
    load_language("en_CA", "some domain", path)


def test_load_language_should_accept_a_local_path_of_type_traversable() -> None:
    traversable = files(__name__)
    load_language("en_CA", "some domain", traversable)


def test_load_language_should_require_the_locale_argument() -> None:
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        load_language(domain="some domain", locale_path="some path")  # type: ignore [call-arg]


def test_load_language_should_require_the_domain_argument() -> None:
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        load_language(locale="en_CA", locale_path="some path")  # type: ignore [call-arg]


def test_load_language_should_require_the_locale_path_argument() -> None:
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        load_language(locale="en_CA", domain="some domain")  # type: ignore [call-arg]


def test_load_language_should_return_a_gettext_fn_and_a_translations_instance() -> None:
    _, t = load_language("en_CA", "some domain", "some path")
    assert hasattr(_, "__func__")
    # Had to do it this way because id(t.gettext) != id(t.gettext). O_o
    assert _.__func__.__name__ == "gettext"  # type: ignore [misc]
    assert isinstance(t, NullTranslations)


def test_load_language_should_validate_the_locale() -> None:
    with pytest.raises(UnknownLocaleError, match="unknown locale"):
        load_language("xx_XX", "some domain", "some path")


def test_load_language_should_load_the_correct_translation_catalog() -> None:
    expected = "Je suis traduit"
    _, t = load_language("fr_CA", "test", TEST_LOCALE_PATH)
    translated: str = _("I am translated")
    assert translated == expected


def test_load_language_should_convert_cldr_locale_format_to_posix_format() -> None:
    expected = "Je suis traduit"
    # Hyphen instead of underscore.
    _, t = load_language("fr-CA", "test", TEST_LOCALE_PATH)
    translated: str = _("I am translated")
    assert translated == expected


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("zh_TW", "I am in zh_Hant_TW"),
        # This is not a legitimate locale, it is just for testing.
        ("ca_Latn_ES_valencia@euro", "I am just ca_ES"),
    ],
)
def test_load_language_should_normalize_the_locale(locale: str, expected: str) -> None:
    _, t = load_language(locale, "test", TEST_LOCALE_PATH)
    translated: str = _("I am translated")
    assert translated == expected


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("kk_Cyrl_KZ", "I am just kk_Cyrl"),
        ("sr_Latn_ME", "I am just sr"),
        ("pt_MZ", "I am just pt"),
    ],
)
def test_load_language_should_enable_falling_back_to_less_precise_translations(
    locale: str, expected: str
) -> None:
    _, t = load_language(locale, "test", TEST_LOCALE_PATH)
    translated: str = _("I am translated")
    assert translated == expected


def test_load_language_should_fall_back_to_the_default_locale() -> None:
    expected = "I am translated"
    _, t = load_language("bas_CM", "test", TEST_LOCALE_PATH)
    translated: str = _("I am translated")
    assert translated == expected


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("fr_CA", "fr_CA"),
        ("zh_TW", "zh_Hant_TW"),
        # This is not a legitimate locale, it is just for testing.
        ("ca_Latn_ES_valencia@euro", "ca_ES"),
        ("kk_Cyrl_KZ", "kk_Cyrl"),
        ("sr_Latn_ME", "sr"),
        ("pt_MZ", "pt"),
    ],
)
def test_load_language_should_log_the_actual_loaded_language(
    logot: Logot, locale: str, expected: str
) -> None:
    _, t = load_language(locale, "test", TEST_LOCALE_PATH)
    logot.assert_logged(
        logged.debug(f"Attempting to load translations for locale: {locale}")
        >> logged.debug(f"Loaded translations for locale: {expected}")
    )


def test_load_language_should_log_when_no_translations_found(logot: Logot) -> None:
    _, t = load_language("bas_CM", "test", TEST_LOCALE_PATH)
    logot.assert_logged(
        logged.debug("Attempting to load translations for locale: bas_CM")
        >> logged.debug("No translations found for locale bas_CM, using defaults")
    )
