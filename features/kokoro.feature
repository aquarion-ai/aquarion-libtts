# SPDX-FileCopyrightText: 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
# SPDX-License-Identifier: CC-BY-SA-4.0

Feature: Kokoro TTS

    As a Aquarion libtts user
    I want to use the Kokoro TTS Model to generate speech from text
    So that I can provide text-to-speech functionality in my application

    Background:
        Given I have loaded and enabled the Kokoro plugin

    Scenario Outline: Getting Display Names in Supported Locales
        When I get the display name for <locale>
        Then I expect the result to be <expected>

        Examples:
            | locale | expected |
            | en_CA  | Kokoro   |
            | en_GB  | Kokoro   |
            | en_US  | Kokoro   |
            | fr_CA  | Kokoro   |
            | fr_FR  | Kokoro   |

    Scenario: Using an NVIDIA GPU
        When I create settings with 'device' set to 'cuda'
        And I create the Kokoro backend using the settings
        And I start the backend
        Then the model should be loaded in the GPU

    Scenario: Using the CPU
        When I create settings with 'device' set to 'cpu'
        And I create the Kokoro backend using the settings
        And I start the backend
        Then the model should be loaded in the CPU

    @todo: Refine me later
    Scenario Outline: Changing the Locale and/or Voice
        When I create default settings
        And I create the Kokoro backend using the settings
        And I start the backend
        And I update the settings to <locale> and <voice>
        Then the backend should use the new settings values

        Examples:
            | locale | voice    |
            | en_CA  | af_heart |
            | en_GB  | bf_emma  |
            | fr_CA  | ff_siwis |

    @todo: Refine me later
    Scenario: Changing the Speed
        When I create settings with 'speed' set to '1.0'
        And I create the Kokoro backend using the settings
        And I start the backend
        And I update the 'speed' setting to '0.5'
        Then the backend should use the new settings values

    Scenario: Converting Text to Speech
        When I create default settings
        And I create the Kokoro backend using the settings
        And I start the backend
        Then converting text to speech should work as expected

    Scenario: Checking for GPU Memory Leaks
        When I create default settings
        And I create the Kokoro backend using the settings
        And I start the backend
        And I convert text to speech '30' times in a row
        Then GPU memory usage remain consistent

    Scenario: Working Offline with No Network
        When I create settings with paths to pre-existing local files
        And I create the Kokoro backend using the settings
        And I start the backend
        Then no network downloading occurs
