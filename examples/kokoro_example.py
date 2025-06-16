# noqa: INP001
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


"""An example of using the Kokoro TTS backend of aquarion-libtts."""

import wave
from warnings import filterwarnings

from aquarion.libs.libtts.api import TTSPluginRegistry

filterwarnings(
    action="ignore",
    message="dropout option adds dropout after all but last recurrent layer",
    category=UserWarning,
)
filterwarnings(
    action="ignore",
    message="`torch.nn.utils.weight_norm` is deprecated",
    category=FutureWarning,
)

registry = TTSPluginRegistry()
registry.load_plugins(validate=True)

print("loaded plugins:")  # noqa: T201
for plugin_id in registry.plugin_ids:
    print("  -", plugin_id, "| Enabled:", registry.is_enabled(plugin_id))  # noqa: T201

registry.enable("kokoro_v1")
plugin = registry.get_plugin("kokoro_v1")

print("Enabled plugin:", plugin.get_display_name("en_CA"))  # noqa: T201

settings = plugin.make_settings()
backend = plugin.make_backend(settings)

print("Format:", str(backend.audio_spec))  # noqa: T201
print("Starting...")  # noqa: T201

try:
    backend.start()

    with wave.open("play_me.wav", "wb") as wave_file:
        wave_file.setnchannels(backend.audio_spec.num_channels)
        wave_file.setsampwidth(backend.audio_spec.sample_width // 8)
        wave_file.setframerate(backend.audio_spec.sample_rate)
        for audio_chunk in backend.convert(
            "Hi there from aquarion-libtts.  This is the kokoro backend."
        ):
            wave_file.writeframes(audio_chunk)

finally:
    backend.stop()

print("Done.")  # noqa: T201
print(  # noqa: T201
    "A file named 'play_me.wav' has been created.  "
    "You can play it with 'aplay play_me.wav'."
)
