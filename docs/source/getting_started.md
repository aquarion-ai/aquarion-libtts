# Getting Started

% SPDX-FileCopyrightText: 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
% SPDX-License-Identifier: CC-BY-SA-4.0

% aquarion-libtts documentation © 2025-present by Krys Lawrence is licensed under
% Creative Commons Attribution-ShareAlike 4.0 International. To view a copy of this
% license, visit <https://creativecommons.org/licenses/by-sa/4.0/>

## Installation

aquarion-libtts comes in several different flavours, depending on your needs.  These
variations are handled by specifying extras when installing.

First, there are extras for supporting various GPU platforms:

- `cpu`: Include PyTorch, but only support CPU and not any GPUs.
- `cu128`: Include PyTorch with CUDA 12.8 support for Nvidia GPUs.
- `cu129`: Include PyTorch with CUDA 12.9 support for Nvidia GPUs.

Second, each built-in TTS backend has it's own extra so that only the dependencies of
the TTS plugins you want to use will be included:

- `kokoro`: Include the required dependencies for Kokoro TTS.

So, to install only the base package, without support for any of the built-in TTS
backends, you can run something like:

```sh
pip install aquarion-libtts
```

However, in order to use at least one TTS backend, you will probably want to include
some extras like this, for example:

```sh
pip install aquarion-libtts[cu129,kokoro]
```

Or:

```sh
pip install aquarion-libtts[cpu,kokoro]
```

## Built-In TTS Plugins

aquarion-libtts provides (or will provide) built-in support for several TTS backends.
They are accessed through the same plugin API as any third-party TTS backend you might
also use.

The following TTS backends currently have built-in support:

:::{list-table}
:header-rows: 1

- - Plugin ID
  - TTS Backend

- - `kokoro_v1`
  - [Kokoro TTS](https://huggingface.co/hexgrad/Kokoro-82M)

:::

## Basic Usage

### Key Concepts

1. The library uses a plugin system to managed multiple TTS backends.
1. All access to the plugins, their backends and their settings are handled through the
   `api` package.
1. There is a plugin registry that provides access to everything else.
1. All TTS backends provide the same interface so that they can be used interchangeably.
1. Each TTS backend can have different configuration settings, however.

### Step 1: Instantiate the Registry

```python
from aquarion.libs.libtts import api

registry = api.TTSPluginRegistry()
```

### Step 2: Load All Plugins

```python
registry.load_plugins()
```

### Step 3: Enable Desired Plugins

All loaded plugins are disabled by default.  This means that they will not show up in
the list of available plugins.  Plugins that you want to use should be enabled like so:

```python
registry.enable("kokoro_v1")
```

Ideally, plugins should be versioned to allow different implementations over time.

### Step 4: Instantiate a Plugin

```python
plugin = registry.get_plugin("kokoro_v1")
```

Plugins are containers that provide access to their TTS backends and backend-appropriate
settings, as well as methods for describing the backend and it's settings in multiple
languages.  See the below for more details of the descriptive capabilities of plugins.

### Step 5: Instantiate Settings

Each backend is expected to support fully functional default settings, in addition to
customized settings.  To instantiate default settings, do this:

```python
settings = plugin.make_settings()
```

Or, to instantiate more customized settings, do something like this:

```python
settings = plugin.make_settings(from_dict={
    "voice": "af_bella"
})
```

Settings are only ever set using a dictionary, not through setting attributes directly.
Also, settings objects are immutable once created, so changing settings requires
creating a whole new settings instance.  This is meant to facilitate the saving and
loading of backend settings in a consistent way, as well as make it easier for dynamic
settings UIs to be created.

### Step 6: Instantiate the TTS Backend

```python
backend = plugin.make_backend(settings)
```

TTS backends always require a settings object, even if it is the default settings.
Also, changing settings in an existing backend requires providing a whole new complete
settings instance, since settings are immutable.

### Step 7: Start the Backend

Now that we finally have our TTS backend, we need to start it:

```python
backend.start()
```

Depending on the specific backend, this could start other threads or processes, or
access external APIs.  It could also download other resources it might need.

### Step 8: Convert Text to Speech

When converting text to speech, the results are provided in chunks of audio via an
iterator.  This better supports streaming and real-time applications.  E.g:

```python
import wave

with wave.open("play_me.wav", "wb") as wave_file:
    wave_file.setnchannels(backend.audio_spec.num_channels)
    wave_file.setsampwidth(backend.audio_spec.sample_width // 8)
    wave_file.setframerate(backend.audio_spec.sample_rate)
    for audio_chunk in backend.convert(
        "Hi there from aquarion-libtts.  This is the kokoro backend."
    ):
        wave_file.writeframes(audio_chunk)
```

As you can see, the TTS backend also provides information about the returned audio
format in it's `.audio_spec` attribute.

### Step 9: Stop the Backend

When shutting down or switching TTS backends, it is important to always stop the backend
to allow it to clean up after itself.

```python
backend.stop()
```

Best practice would be to wrap your code in a `try ... finally` block to ensure the stop
method is always called, even in the case of an error.

## Example

See the [examples](https://github.com/aquarion-ai/aquarion-libtts/tree/main/examples)
sub-directory for examples of how to use this project.

## Beyond the Basics

In addition to the above core functionality, more is provided:

- The plugin registry also includes methods for listing plugins, enabled or otherwise,
  as well as disabling plugins, and checking if a plugin is already enabled.

- Each plugin also includes methods for getting it's display name in multiple languages,
  as well as getting details about each specific setting so that a settings UI can be
  constructed, also in multiple languages.

  (Which languages are supported depends on the plugin.)

- Each settings object also include a method to export the settings as a JSON-compatible
  dict for storage, editing, etc.

- Each backend also includes details about the audio format it emits, as well as a
  check for whether or not it is currently started.

To learn more about these extra capabilities, please see the
<project:api/index.md>.

## Creating Your Own TTS Backends

To learn about creating plugins for your own TTS backend for this project, see
<project:plugins.md>.
