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


"""TTSSettings protocol."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

type JSONSerializableTypes = (
    str
    | int
    | float
    | bool
    | None
    | Sequence[JSONSerializableTypes]
    | Mapping[str, JSONSerializableTypes]
)


@runtime_checkable
class ITTSSettings(Protocol):  # noqa: PLW1641
    """Common interface for all TTS backend settings.

    Implementations of this interface are expected to add their own setting attributes
    for the specific :class:`ITTSBackend` implementation they go with.

    **Note:** There is no expectation that ITTSSettings implementations be immutable or
    hashable, but it's probably a good idea since changes to settings should be done by
    calling :meth:`ITTSPlugin.make_settings` with a changed settings dictionary.

    Example:
        .. code:: python

            class MySettings:
                locale: str = "en"
                voice: str = "bella"
                speed: float = 1.0
                api_key: str
                cache_path: Path

                def __eq__(self, other: object) -> bool:
                    # Your implementation here

                def to_dict(self) -> dict[str, JSONSerializableTypes]:
                    # Your implementation here

    .. automethod:: __eq__

    """

    #: The locale should be a POSIX-compliant (i.e. using underscores) or CLDR-compliant
    #: (i.e. using hyphens) locale string like ``en_CA``, ``zh-Hant``,
    #: ``ca-ES-valencia``, or even ``de_DE.UTF-8@euro``.  It can be as general as ``fr``
    #: or as specific as ``language_territory_script_variant@modifier``.
    locale: str

    def __eq__(self, other: object) -> bool:
        """Return True if all settings values match, False otherwise.

        Args:
            other: The other :class:`ITTSSettings` instance to compare against.

        Returns:
            :obj:`True` if ``other`` is an instance of the same concrete implementation
            of :class:`ITTSSettings` and all the settings values are the same.  False
            otherwise.

        """

    def to_dict(self) -> dict[str, JSONSerializableTypes]:
        """Export all settings as a dictionary of only JSON-serializable types.

        Returns:
            A dictionary where the keys are the setting names and the values are the
            setting values converted as necessary to simple base JSON-compatible types.

        Example:
            .. code:: JSON

                {
                    "locale": "en",
                    "voice": "bella",
                    "speed": 1.0,
                    "api_key": "Your API key here",
                    "cache_path": "Cache path converted to a basic string"
                }

        """


@runtime_checkable
class ITTSSettingsHolder(Protocol):
    """Common interface for objects that accept and contain :class:`ITTSSettings`."""

    def get_settings(self) -> ITTSSettings:
        """Return the current setting in use.

        Returns:
            The current settings in use.

        Note:
            The reason the settings are not just direct attributes is because they are
            to be treated as an all-or-nothing collection.  I.e. individual settings
            attributes should not be individually modified directly on an
            :class:`ITTSSettingsHolder`, but rather the whole settings object should be
            replaced with a new one.

        """

    def update_settings(self, new_settings: ITTSSettings) -> None:
        """Update to the new given settings.

        Args:
            new_settings: The new complete set of settings to start using immediately.

        Raises:
            TypeError: Implementations of this interface should check that they are only
                getting the correct concrete settings class and raise an exception if
                any other kind of :class:`ITTSSettings` is given.

        Note:
            The reason the settings are not just direct attributes is because they are
            to be treated as an all-or-nothing collection.  I.e. individual settings
            attributes should not be individually modified directly on an
            :class:`ITTSSettingsHolder`, but rather the whole settings object should be
            replaced with a new one.

        """


type TTSSettingsSpecEntryTypes = str | int | float
type TTSSettingsSpecType = Mapping[str, TTSSettingsSpecEntry[TTSSettingsSpecEntryTypes]]


@dataclass(frozen=True, kw_only=True)
class TTSSettingsSpecEntry[T: TTSSettingsSpecEntryTypes]:
    """An specification entry describing one setting in an ITTSSettings object.

    Since :class:`ITTSSettings` can contain custom TTS backend specific setting
    attributes, there is a need for a way to describe those setting attributes in a
    standardized way so that settings UIs can be constructed dynamically in applications
    that use aquarion-libtts.  Instances of this class, in a dictionary, for example,
    can provide a specification for how to render settings fields in a UI.

    Instances of this class are immutable once created.

    Example:
        .. code:: python

            spec = {
                "locale": TTSSettingSpecEntry(
                    type=str,
                    min=2,
                    values=frozenset("en", "fr")
                ),
                "voice": TTSSettingSpecEntry(type=str),
                "speed": TTSSettingSpecEntry(type=float, min=0.1, max=1.0),
                "api_key": TTSSettingSpecEntry(type=str),
                "cache_path": TTSSettingSpecEntry(type=str),
            }

    With the example above, one could imagine a UI with multiple text box fields.
    ``locale`` could be a dropdown or a set of radio buttons.  There could be validation
    for valid ranges.  ``speed`` could have up and down arrow buttons to increase and
    decrease the value, and / or react to a mouse's scroll wheel.  Etc.

    """

    #: The type of setting it is.
    #:
    #: This is required.
    #:
    #: Currently supported types: :class:`str`, :class:`int` and :class:`float` only.
    #:
    #: This should be set to the actual type class, **not** a string name of a type.
    #:
    #: Also, only Python basic types should be used.  I.e. **not** classes like
    #: :class:`~pathlib.Path` or :class:`~decimal.Decimal`, etc.
    #:
    type: type[T]

    #: The minimum allowed value or minimum allowed length.
    #:
    #: This is optional.
    #:
    #: For strings this is the minimum allowed length of the string.
    #:
    #: For numeric types, this is the minimum allowed value.
    #:
    min: int | float | None = None

    #: The maximum allowed value or maximum allowed length.
    #:
    #: This is optional.
    #:
    #: For strings this is the maximum allowed length of the string.
    #:
    #: For numeric types, this is the maximum allowed value.
    #:
    max: int | float | None = None

    #: The set of specific allowed values.
    #:
    #: This is optional.
    #:
    #: Some fields might only accept a restricted set of specific valid values.  Think
    #: enumerations.  Acceptable values can be specified with this attribute.
    #:
    values: frozenset[T] | None = None
