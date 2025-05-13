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


"""TTSBackend protocol."""

from typing import Protocol, runtime_checkable

from aquarion.libs.libtts.api._ttssettings import (
    ITTSSettings,
    ITTSSettingsHolder,
    ITTSSettingsHolderFactory,
)
from aquarion.libs.libtts.api._ttsspeechdata import TTSSpeechData


@runtime_checkable
class ITTSBackend(ITTSSettingsHolder, Protocol):
    """Common interface for all TTS backends."""

    def convert(self, text: str) -> TTSSpeechData:
        """Return speech audio generated from the given text."""


@runtime_checkable
class ITTSBackendFactory(ITTSSettingsHolderFactory, Protocol):
    """Common interface for all TTSBackend factories."""

    @staticmethod
    def __call__(settings: ITTSSettings) -> ITTSBackend:
        """Return an object that conforms to the ITTSBackend protocol.

        Custom or default settings must be provided to configure the TTS backend.

        Implementations of this interface should check that they are only getting the
        correct concrete settings class and raise TypeError if any other kind of
        concrete ITTSSettings is given.
        """
