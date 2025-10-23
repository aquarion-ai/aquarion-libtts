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
"""Basic Python types that are easily serializable to JSON."""


type TTSSettingsSpecEntryTypes = str | int | float
"""Valid types for a settings spec entry.

[TTSSettingsSpecEntry][aquarion.libs.libtts.api.TTSSettingsSpecEntry] types must be one
of these types.

"""

type TTSSettingsSpecType = Mapping[str, TTSSettingsSpecEntry[TTSSettingsSpecEntryTypes]]
"""The type of the TTS settings spec mapping.

[ITTSPlugin.make_spec][aquarion.libs.libtts.api.ITTSPlugin.get_settings_spec] returns
this.

"""


@runtime_checkable
class ITTSSettings(Protocol):  # noqa: PLW1641
    """Common interface for all TTS backend settings.

    Implementations of this interface are expected to add their own setting attributes
    for the specific [ITTSBackend][aquarion.libs.libtts.api.ITTSBackend] implementation
    they go with.

    Note:
        There is no expectation that ITTSSettings implementations be immutable or
        hashable, but it's probably a good idea since changes to settings should be done
        by calling the
        [ITTSPlugin.make_settings][aquarion.libs.libtts.api.ITTSPlugin.make_settings]
        method with a changed settings dictionary.

    Example:
        ```python linenums="1"
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
        ```

    """

    locale: str
    """The locale for spoken audio language.

    The locale should be a POSIX-compliant (i.e. using underscores) or CLDR-compliant
    (i.e. using hyphens) locale string like `en_CA`, `zh-Hant`, `ca-ES-valencia`, or
    even `de_DE.UTF-8@euro`.  It can be as general as `fr` or as specific as
    `language_territory_script_variant@modifier`.

    """

    def __eq__(self, other: object) -> bool:
        """Check if two settings objects are equal.

        Args:
            other: The other [ITTSSettings][aquarion.libs.libtts.api.ITTSSettings]
                instance to compare against (or any other Python object).

        Returns:
            [True][] if `other` is an instance of the same concrete settings class *and*
                all the settings values are the same.

                [False][] otherwise.

        """

    def to_dict(self) -> dict[str, JSONSerializableTypes]:
        """Export all settings as a dictionary of only JSON-serializable types.

        Returns:
            A dictionary where the keys are the setting names and the values are the
                setting values converted as necessary to simple base JSON-compatible
                types.

        Example:
            ```json
            {
                "locale": "en",
                "voice": "bella",
                "speed": 1.0,
                "api_key": "Your API key here",
                "cache_path": "Cache path converted to a basic string"
            }
            ```
            &nbsp;

        """
        # Note: &nbsp; is included above because there seems to be a bug in ruff fmt
        #       when a JSON code block is at the end of a docstring.  (v0.14.0)


@runtime_checkable
class ITTSSettingsHolder(Protocol):
    """Common interface for objects that accept and contain settings."""

    def get_settings(self) -> ITTSSettings:
        """Return the current setting in use.

        Returns:
            The current settings in use.

        Note:
            The reason the settings are not just direct attributes is because they are
            to be treated as an all-or-nothing collection.  I.e. individual settings
            attributes should not be individually modified directly on an
            [ITTSSettingsHolder][aquarion.libs.libtts.api.ITTSSettingsHolder], but
            rather the whole settings object should be replaced with a new one.

        """

    def update_settings(self, new_settings: ITTSSettings) -> None:
        """Update to the new given settings.

        Args:
            new_settings: The new complete set of settings to start using immediately.

        Raises:
            TypeError: Implementations of this interface should check that they are only
                getting the correct concrete settings class and raise an exception if
                any other kind of [ITTSSettings][aquarion.libs.libtts.api.ITTSSettings]
                is given.

        Note:
            The reason the settings are not just direct attributes is because they are
            to be treated as an all-or-nothing collection.  I.e. individual settings
            attributes should not be individually modified directly on an
            [ITTSSettingsHolder][aquarion.libs.libtts.api.ITTSSettingsHolder], but
            rather the whole settings object should be replaced with a new one.

        """


@dataclass(frozen=True, kw_only=True)
class TTSSettingsSpecEntry[T: TTSSettingsSpecEntryTypes]:
    """An specification entry describing one setting of a settings object.

    Since [ITTSSettings][aquarion.libs.libtts.api.ITTSSettings] can contain custom TTS
    backend specific setting attributes, there is a need for a way to describe those
    setting attributes in a standardized way so that settings UIs can be constructed
    dynamically in applications that use *aquarion-libtts*.  Instances of this class, in
    a dictionary, for example, can provide a specification for how to render settings
    fields in a UI.

    Example:
        ```python
        spec = {
            "locale": TTSSettingSpecEntry(
                type=str, min=2, values=frozenset("en", "fr")
            ),
            "voice": TTSSettingSpecEntry(type=str),
            "speed": TTSSettingSpecEntry(type=float, min=0.1, max=1.0),
            "api_key": TTSSettingSpecEntry(type=str),
            "cache_path": TTSSettingSpecEntry(type=str),
        }
        ```

        With the example above, one could imagine a UI with multiple text box fields.
        `locale` could be a dropdown or a set of radio buttons, there could be
        validation for valid ranges, `speed` could have up and down arrow buttons to
        increase and decrease the value, and / or react to a mouse's scroll wheel, etc.

    Note:
        Instances of this class are immutable once created, as are all the attribute
        values as well.

    """

    type: type[T]
    """The type of setting it is.

    This is required.

    Valid types are defined in
    [TTSSettingsSpecEntryTypes][aquarion.libs.libtts.api.TTSSettingsSpecEntryTypes].

    Notes:
        - This should be set to the actual type class, **not** a string name of a type.

        - Also, only Python basic types should be used.  I.e. **not** classes like
          [pathlib.Path][] or [decimal.Decimal][], etc.

    """

    min: int | float | None = None
    """The minimum allowed value or minimum allowed length.

    This is optional.

    For strings this is the minimum allowed length of the string.

    For numeric types, this is the lowest allowed value.

    """

    max: int | float | None = None
    """The maximum allowed value or maximum allowed length.

    This is optional.

    For strings this is the maximum allowed length of the string.

    For numeric types, this is the highest allowed value.

    """

    values: frozenset[T] | None = None
    """The set of specific allowed values.

    This is optional.

    Some fields might only accept a restricted set of specific valid values.  Think
    enumerations.  Acceptable values can be specified with this attribute.

    """
