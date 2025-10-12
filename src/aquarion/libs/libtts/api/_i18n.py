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

from __future__ import annotations

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
    """PathLikes are hashable, but this makes it explicit for the type checker."""


class HashableTraversable(Hashable, Traversable):
    """Traversables are hashable, but this makes it explicit for the type checker."""


@cache  # type:ignore[misc]
def load_language(
    locale: str, domain: str, locale_path: HashablePathLike | HashableTraversable | str
) -> LoadLanguageReturnType:
    """Return a :mod:`gettext` ``_()`` function and a ``*Translations`` instance.

    Args:
        locale:
            The desired locale to find and load.  E.g. ``en_CA`` or `fr``, etc.

            ``locale`` must be parsable by the `Babel`_ package and will be normalized
            by it as well.

            ``locale`` is generally expected to be in POSIX format (i.e. using
            underscores) but CLDR format (i.e. using hyphens) is also supported and will
            be converted to POSIX format automatically for the purpose of finding
            translation catalogues.

            If an exact match on locale cannot be found, less specific fallback locales
            well be used instead.  E.g. if ``kk_Cyrl_KZ`` is not found, then ``kk_Cyrl``
            will be tried, and then just ``kk``.

            If no matching locale is found, then the gettext methods will just return
            the hard coded strings from the source file.

        domain:
            A name unique to your app / project.  This domain name becomes the file
            name of your message catalogues and templates.  For example you you could
            your project's name or your root package's name.  E.g. ``my-cool-project``.

            .. note::
                Do not use ``aquarion-libtts`` as your domain name.  That is reserved
                for this project.

        locale_path:
            The base path where your language files can be found.  This can be
            a regular path (as a :class:`str` or a :class:`~pathlib.Path`) or this
            could be some path inside your own Python package, retrieved with the help
            of :func:`importlib.resources.files`, for example.

            .. note::
                It is recommended that third-party :doc:`TTS plugins <../plugins>` keep
                their translation files inside their package (i.e. wheel) by using
                :func:`importlib.resources.files` to access a locale directory.

    Returns:
        A :class:`tuple` of (a :meth:`~gettext.GNUTranslations.gettext` callable, a
        :class:`~gettext.GNUTranslations` instance).

        The ``gettext`` callable is provided for easy use of the more common action.

        The ``*Translations`` instance provides access to all the other, less common
        translation capabilities one might need, e.g. ``ngettext``, ``pgettext``, etc.

        .. attention::
            It is common practice to name the ``gettext`` callable ``_``, so that
            extracting and retrieving translated messages is as easy is ``_("text to be
            translated")``.  In fact, if you use `Babel`_ this will be expected by
            default for translatable strings to be found.

    Raises:
        various: If an invalid locale is given various possible exceptions can be
            raised.  See Babel package's :external+babel:meth:`babel.core.Locale.parse`
            for details..

    Example:
        .. code:: python

            from importlib.resources import files
            from typing import cast

            from aquarion.libs.libtts.api import HashableTraversable

            locale_path = cast(HashableTraversable, files(__name__) / "locale")
            _, t = load_language(
                "fr_CA",
                domain="my-cool-project",
                locale_path=locale_path
            )
            print(_("I will be translated"))

    Note:
        Once loaded, the language translations are cached for the duration of the
        process.

    .. _Babel: https://babel.pocoo.org/

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
