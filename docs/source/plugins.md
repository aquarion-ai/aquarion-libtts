# Adding Custom TTS Plugins

% SPDX-FileCopyrightText: 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
% SPDX-License-Identifier: AGPL-3.0-only

% Part of the aquarion-libtts library of the Aquarion AI project.
% Copyright (C) 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>

% This program is free software: you can redistribute it and/or modify it under the
% terms of the GNU Affero General Public License as published by the Free Software
% Foundation, version 3.

% This program is distributed in the hope that it will be useful, but WITHOUT ANY
% WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
% PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

% You should have received a copy of the GNU Affero General Public License along with
% this program. If not, see <https://www.gnu.org/licenses/>.

## Overview

aquarion-libtts provides all it's TTS backends through a plugin system.  This also means
that you can create your own 3rd-party TTS plugins in your own external packages and
they will also be loaded and usable within aquarion-libtts.

To create a TTS backend plugin, the following components are required:

<!--
  As of Sphinx 8.2.3, the py:deco role does not support the ~ modifier.  This will be
  fixed in 8.3.0.  So for now, I am using py:obj instead for tts_hookimpl.
-->
- An implementation of the {class}`~aquarion.libs.libtts.api.ITTSSettings` protocol,
- An implementation of the {class}`~aquarion.libs.libtts.api.ITTSBackend` protocol,
- An implementation of the {class}`~aquarion.libs.libtts.api.ITTSPlugin` protocol,
- A {obj}`~aquarion.libs.libtts.api.tts_hookimpl` decorated function to register your
  plugin, and
- An `aquarion-libtts`
  [entry point](https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-package-metadata)
  in your `pyproject.toml` file.

Additionally, since multi-lingual support is expected by default, you should also
include some `gettext` catalogues and design for internationalization and localization
from your first release. The {func}`~aquarion.libs.libtts.api.load_language` function
can help with that.  ... Though, this is not *strictly* required, it is best practice.

## How the Plugin System Works

<!--
  As of Sphinx 8.2.3, the py:deco role does not support the ~ modifier.  This will be
  fixed in 8.3.0.  So for now, I am using py:obj instead for tts_hookimpl.
-->
1. When you call the {meth}`~aquarion.libs.libtts.api.TTSPluginRegistry.load_plugins`
   method, all installed packages are searched for `aquarion-libtts` entry points.

1. Each found entry point is then searched for
   {obj}`~aquarion.libs.libtts.api.tts_hookimpl` functions.

1. Each found {obj}`~aquarion.libs.libtts.api.tts_hookimpl` function is then called and
   is expected to either return an instance of an
   {class}`~aquarion.libs.libtts.api.ITTSPlugin` implementation, or {obj}`None` if no
   plugin is to be registered.  E.g. There are missing dependencies, incompatible
   hardware, etc.

1. All the returned plugin instances are then registered in the
   {class}`~aquarion.libs.libtts.api.TTSPluginRegistry` for potential use.

   **Note:** They are all in a *disabled* state to start.  Meaning they are not listed
   as available plugins until each desired plugin is explicitly enabled.  This allows
   for controlling the list of available plugins independently of which ones are
   installed.

1. Through the registry, plugins can be retrieved and used.

## The Entry Point

aquarion-libtts TTS plugins are found by searching installed packages for
[PEP 621](https://peps.python.org/pep-0621/#entry-points)-style entry points, or more
accurately entry-points as defined in the
[pyproject.toml specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/#entry-points).

Specifically, add something like this to your `pyproject.toml` file:

```toml
[project.entry-points.'aquarion-libtts']
my_plugin_v1 = "package.hook"
```

Where:

'aquarion-libtts'
: Is the entry point group name for all aquarion-libtts entry points.

my_plugin
: Is the unique identifier key for your plugin.  E.g. `kokoro`

_v1
: Is the major version of your plugin.  This is so that old implementations and new ones
  can exist at the same time for backward compatibility.

package.hook
: Is the module in your package that contains your
  {obj}`~aquarion.libs.libtts.api.tts_hookimpl` decorated plugin registration function.

## The Registration Function

aquarion-libtts plugins are registered by creating a hook function that:

1. Is decorated by the {obj}`~aquarion.libs.libtts.api.tts_hookimpl` decorator.
1. Returns an instance of an {class}`~aquarion.libs.libtts.api.ITTSPlugin`
   implementation or {obj}`None` to skip registering anything.

For example:

```python
from aquarion.libs.libtts.api import ITTSPlugin, tts_hookimpl

@tts_hookimpl
def register_my_tts_plugin() -> ITTSPlugin | None:
    """Return an instance of my TTS plugin if the dependencies are installed."""
    # NOTE: It is important that we do not import our plugin class or related packages
    #       at module import time.
    #       This hook needs to be able to run even when our required dependencies, etc.
    #       are not installed.
    try:
        import dependency
    except ModuleNotFoundError:
        return None
    from package.plugin import MyTTSPlugin

    return MyTTSPlugin()
```

## The Plugin

An aquarion-libtts TTS plugin is responsible for creating, configuring and describing
a TTS backend in a consistent way.  Specifically, it is responsible for:

- Creating TTS backend-specific settings objects,
- Creating TTS backend objects themselves,
- Providing multi-lingual metadata for UI presentation such as:
  - The plugin/backend's display name,
  - Specifications for all attribute in the settings object, such as type, valid
    values, and/or minimum and maximum valid range of values, where applicable.
  - Display names for each attribute in the settings object.
  - Descriptions for each attribute in the settings object.

To fulfil these requirements, a TTS plugin must implement the
{class}`~aquarion.libs.libtts.api.ITTSPlugin` protocol.

## The Settings

On the one hand, each TTS backend likely needs it's own custom settings, unique to the
specific backend.  Also, TTS backend settings could be different for different locales.
On the other hand, the settings objects for all TTS backends need to be exportable /
savable / transmittable in a standardized way.

To fulfil these requirements, a TTS settings object must implement the
{class}`~aquarion.libs.libtts.api.ITTSSettings` protocol.  But in addition to that, it
can have additional custom attributes.

Also, while it is the responsibility of the
{meth}`~aquarion.libs.libtts.api.ITTSPlugin.make_settings` factory method to validate
any settings object it creates, it is also reasonable for
{class}`~aquarion.libs.libtts.api.ITTSSettings` implementations to validate themselves
on creation, if desired.  Though this not not strictly required.

Lastly, the {meth}`~aquarion.libs.libtts.api.ITTSPlugin.make_settings` factory method
must also support returning a fully functional TTS settings object with all default
values when called with no arguments.  So, it is also not unreasonable for
{class}`~aquarion.libs.libtts.api.ITTSSettings` implementations to also include fully
functional default values on instantiation.  Though this not not strictly required.

## The Backend

Finally, there is the TTS backend object itself.  This is the main object.  It is
responsible for converting text input in to an audio stream output.  It is also
responsible for reporting the kind of audio it produces (e.g. raw PCM, WAVE, MP3, OGG,
VP8, stereo, mono, 8-bit, 16-bit, etc.).  Client software is expected to support
whatever formats their chosen supported backends produce.

To fulfil these requirements, a TTS backend object must implement the
{class}`~aquarion.libs.libtts.api.ITTSBackend` protocol.

TTS backends work on the concept that they need to be started before being used, and
then stopped when they are no longer required.  So, it is recommended to wrap the the
call to {meth}`~aquarion.libs.libtts.api.ITTSBackend.start` in a `try ... finally` block
to ensure that {meth}`~aquarion.libs.libtts.api.ITTSBackend.stop` always gets called on
shutdown.

Additionally, it would not be unreasonable for a TTS backend to access external APIs or
download additional resources once started, however, those activities should not be done
on instantiation, only on startup.

## Putting It All Together

So, in summary:

1. Client software creates a plugin registry.
1. The registry finds your entry point and calls your registration function to collect
   your plugin.
1. Client software enables your plugin.
1. Client software fetches your plugin from the registry.
1. Client software asks your plugin to make your settings object.
1. Client software asks your plugin to make your backend object using the above
   settings.
1. Client software starts your backend.
1. Client software uses your backend to convert text to speech.
1. Client software stops your backend.
1. Client software optionally can also ask your plugin about various metadata.
1. Client software optionally can save and load dictionaries of preferred settings
   values.
1. Client software optionally can re-configure your backend with new a settings object
   as created by your plugin.

That's it.  By following this pattern, various diverse TTS systems can be implemented,
installed and used in various client software designs.
