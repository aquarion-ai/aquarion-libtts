# Kokoro Backend

<!-- markdownlint-disable MD052 -->

## Description

From [Kokoro on HuggingFace](https://huggingface.co/hexgrad/Kokoro-82M):

> Kokoro is an open-weight TTS model with 82 million parameters. Despite its lightweight
> architecture, it delivers comparable quality to larger models while being
> significantly faster and more cost-efficient. With Apache-licensed weights, Kokoro can
> be deployed anywhere from production environments to personal projects.

## Supported Languages / Locales

You can find the languages and locales that the *aquarion-libtts* Kokoro Backend
supports un the [KokoroLocales][aquarion.libs.libtts.kokoro.settings.KokoroLocales]
class in the API Reference.

## Prerequisites

Kokoro requires [espeak-ng](https://github.com/espeak-ng/espeak-ng)
be installed on your system.  See
[espeak-ng's documentation](https://github.com/espeak-ng/espeak-ng/blob/master/docs/guide.md#installation)
for installation instructions.

## Configuration Settings

You can find the specific settings that the *aquarion-libtts* Kokoro Backend accepts in
the [KokoroSettings][aquarion.libs.libtts.kokoro.settings.KokoroSettings] class in the
API Reference.

## Offline / Air-Gapped Support

Normally, Kokoro will automatically download and cache any files it needs from the
Internet (e.g. models, configuration, voices, etc.).  However it also supports working
in a fully offline or air-gapped environment if configured properly.  To use the Kokoro
Backend in this way, do the following:

1. Manually download the following files from the
  [Kokoro HuggingFace repository](https://huggingface.co/hexgrad/Kokoro-82M/tree/main):

    - `kokoro-v1_0.pth`: The actual model (approx. 330 MiB)
    - `config.json`: The model's configuration
    - `voices/*.pt`: Download whichever supported voice(s) you want
        - The list of voices supported by *aquarion-libtts* can be found in the
          [KokoroVoices][aquarion.libs.libtts.kokoro.settings.KokoroVoices] class.

1. Put the above files together in a known location on your offline / air-gapped machine
   so that the Kokoro Backend can be configured to find them.

1. Also required is the [spaCy en_core_web_sm](https://spacy.io/models/en/#en_core_web_sm)
   model (regardless of locale / language).  You can download this in one of two ways:

    *Either:*

    - Run `python -m spacy download en_core_web_sm` while connected to the Internet and
      then disconnect from the Internet,

    *Or:*

    - Manually download the Python wheel (`.whl` file) distribution for `en_core_web_sm`
      from [GitHub](https://github.com/explosion/spacy-models/releases?q=en_core_web_sm&expanded=true)
      and then install it on the offline / air-gapped machine using `pip` or `uv` or
      whatever you prefer.

    !!! attention
        Currently *aquarion-libtts* supports `en_core_web_sm` version
        **{{ en_core_web_sm_version }}**, so that is the recommended version to use.

1. Lastly, in your code, when you call the Kokoro plugin's
   [make_settings][aquarion.libs.libtts.api.ITTSPlugin.make_settings] factory method,
   you must configure it using `from_dict` to set the following settings:

    - [model_path][aquarion.libs.libtts.kokoro.settings.KokoroSettings.model_path]
    - [config_path][aquarion.libs.libtts.kokoro.settings.KokoroSettings.config_path]
    - [voice_path][aquarion.libs.libtts.kokoro.settings.KokoroSettings.voice_path]

    This way the Kokoro Backend will know where to find what it needs locally and will
    not reach out to the Internet.

    !!! note
        Also, whenever your code changes the voice, it will have to to it by changing
        the [voice_path][aquarion.libs.libtts.kokoro.settings.KokoroSettings.voice_path]
        setting instead of the `voice` setting.
