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

"""Kokoro TTS hook implementation."""

from aquarion.libs.libtts.api import ITTSPlugin, tts_hookimpl


@tts_hookimpl
def register_tts_plugin() -> ITTSPlugin | None:
    """Return the Kokoro TTS plugin if Kokoro TTS is installed."""
    # NOTE: It is important that we do not import KokoroPlugin or related at module
    #       import time.
    #       This hook needs to be able to run even when Kokoro and PyTorch, etc. are not
    #       installed.
    #       I.e. if the [kokoro] & [cu128] extras are not installed, we just skip
    #       registering the KokoroPlugin.
    try:
        import kokoro  # noqa: F401
        import torch  # noqa: F401
    except ModuleNotFoundError:
        return None
    from aquarion.libs.libtts._kokoro._plugin import KokoroPlugin

    return KokoroPlugin()
