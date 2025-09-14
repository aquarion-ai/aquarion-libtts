# SPDX-FileCopyrightText: 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
# SPDX-License-Identifier: CC-BY-SA-4.0

@kokoro
Feature: Kokoro TTS
    As a software developer
    I want to use the Kokoro TTS Model to generate speech from text
    So that I can provide text-to-speech functionality in my application

    Background:
        Given I have a TTSBackendRegistry
        And I have loaded all available plugins
        And I am using the 'kokoro_v1' plugin

    @gpu
    Scenario: Using an NVIDIA GPU
        When I make settings with 'device' set to 'cuda'
        And I make the backend using the settings
        And I measure baseline GPU memory usage
        And I start the backend
        Then the model should be loaded in the GPU

    Scenario: Using the CPU
        When I make settings with 'device' set to 'cpu'
        And I make the backend using the settings
        And I measure baseline GPU memory usage
        And I start the backend
        Then the model should be loaded in the CPU

    Scenario Outline: Changing the Locale and/or Voice
        When I make the default settings for the backend
        And I make the backend using the settings
        And I start the backend
        And I make new settings using <locale> and <voice>
        And I update the backend with the new settings
        Then the backend should use the new settings

        Examples:
            | locale | voice    |
            | en_CA  | af_heart |
            | en_GB  | bf_emma  |
            | fr_CA  | ff_siwis |

    Scenario: Changing the Speed
        When I make settings with 'speed' set to '1.0'
        And I make the backend using the settings
        And I start the backend
        And I make new settings with 'speed' set to '0.5'
        And I update the backend with the new settings
        Then the backend should use the new settings

    Scenario: Converting Text to Speech
        When I make the default settings for the backend
        And I make the backend using the settings
        And I start the backend
        And I convert 'Hi there!' to speech
        Then the audio output should be as expected

    @gpu
    Scenario: Checking for GPU Memory Leaks
        When I make settings with 'device' set to 'cuda'
        And I make the backend using the settings
        And I measure baseline GPU memory usage
        And I start the backend
        And I convert text to speech '30' times in a row
        Then GPU memory usage remain consistent

    Scenario: Working Offline with No Network
        When I make settings with paths to pre-existing local files
        And I make the backend using the settings
        And I start the backend
        Then no network downloading occurs
