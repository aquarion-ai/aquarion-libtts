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


"""Utilities to help with internationalization and localization."""

from collections.abc import Callable, Hashable
from functools import cache
from gettext import NullTranslations, translation
from importlib.resources import as_file
from importlib.resources.abc import Traversable
from os import PathLike

from babel import Locale
from loguru import logger

type GettextFuncType = Callable[[str], str]
type LoadLanguageReturnType = tuple[GettextFuncType, NullTranslations]


class HashablePathLike(Hashable, PathLike[str]):
    """PathLikes are hashable, but his makes it explicit for the type checker."""


class HashableTraversable(Hashable, Traversable):
    """Traversables are hashable, but this makes it explicit for the type checker."""


@cache  # type:ignore[misc]
def load_language(
    locale: str, domain: str, locale_path: HashablePathLike | HashableTraversable | str
) -> LoadLanguageReturnType:
    """Return a gettext _() function and a Translations instance.

    locale must be parsable by the Babel package and will be normalized by it as well.

    locale is generally expected to be in POSIX format (i.e. using underscores) but
    CLDR format (i.e. using hyphens) is also supported and will be converted to POSIX
    format automatically for the purpose of finding translation catalogues.

    It is recommended that TTS plugins keep their translation files inside their
    package (i.e. wheel) by using importlib.resources.files() to access a locale
    directory.

    If an exact match on locale cannot be found, less specific fallback locales well be
    used instead.  E.g. if `kk_Cyrl_KZ` is not found, then `kk_Cyrl` will be tried, and
    then just `kk`.

    If no matching locale is found, then the gettext methods will just return the hard
    coded strings from the source file.

    Raises various exceptions if an invalid locale is given, as determined by the Babel
    package's Local.parse() method.

    Note: Once loaded, the language translations are cached for the duration of the
    process.
    """
    logger.debug(f"Attempting to load translations for locale: {locale}")
    loc = Locale.parse(locale, sep="-") if "-" in locale else Locale.parse(locale)
    # 1. Locale will strip out variants and modifiers automatically, so we do not need
    #    to handle those.
    # 2. gettext will automatically fall back to just the 2-letter language if it is
    #    available, so we do not need to handle that either.
    # 3. But, falling back from language_script_territory to just language_script is NOT
    #    handled automatically, so we need to do that ourselves.
    locales = [str(loc)]
    if loc.script and loc.territory:
        loc.territory = None
        locales.append(str(loc))
    if isinstance(locale_path, Traversable):
        with as_file(locale_path) as real_locale_path:
            translations = translation(domain, real_locale_path, locales, fallback=True)
    else:
        translations = translation(domain, locale_path, locales, fallback=True)
    try:
        logger.debug(
            f"Loaded translations for locale: {translations.info()['language']}"
        )
    except KeyError:
        logger.debug(f"No translations found for locale {loc}, using defaults")
    return translations.gettext, translations
