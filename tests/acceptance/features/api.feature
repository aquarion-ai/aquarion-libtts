# SPDX-FileCopyrightText: 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
# SPDX-License-Identifier: CC-BY-SA-4.0

@api
Feature: TTS Library Interface
    As a software developer
    I want to access various TTS backend implementations using a common API
    So that the backends can be replaced in a modular or even dynamic way.

    Background:
        Given I have a TTSBackendRegistry
        And I have loaded all available plugins

    Scenario: Discover all available plugins
        When I list all plugins IDs
        Then I should see the following plugin IDs:
            | plugin_id |
            | kokoro_v1 |

    Scenario: Enable some plugins
        When I enable the following plugins:
            | plugin_id |
            | kokoro_v1 |
        Then the plugins should be enabled

    Scenario: Disable some plugins
        When I disable the following plugins:
            | plugin_id |
            | kokoro_v1 |
        Then the plugins should be disabled

    Scenario: List enabled plugins
        When I enable the following plugins:
            | plugin_id |
            | kokoro_v1 |
        And I list the plugin IDs
        Then I should see only the enabled plugins

    Scenario: List disabled plugins
        When I disable the following plugins:
            | plugin_id |
            | kokoro_v1 |
        # And I enable the following plugins:
        #     | plugin_id   |
        #     | future_todo |
        And I list the disabled plugin IDs
        Then I should see the disabled plugins
    #   And I should not see the enabled plugins

    Scenario: All plugins are disabled by default
        When no plugins are explicitly enabled
        And I list the plugin IDs
        Then I should see no plugins

    Scenario Outline: Get a plugin's display name for a locale
        Given I am using the <plugin_id> plugin
        When I get the display name for <locale>
        Then I see <display_name>

        Examples:
            | plugin_id | locale | display_name |
            | kokoro_v1 | en_CA  | Kokoro       |
            | kokoro_v1 | en_US  | Kokoro       |
            | kokoro_v1 | en_GB  | Kokoro       |
            | kokoro_v1 | en     | Kokoro       |
            | kokoro_v1 | fr_CA  | Kokoro       |
            | kokoro_v1 | fr_FR  | Kokoro       |
            | kokoro_v1 | fr     | Kokoro       |

    Scenario Outline: Make a backend with default settings
        Given I am using the <plugin_id> plugin
        When I make the default settings for the backend
        And I make the backend using the settings
        Then the backend should use the given settings

        Examples:
            | plugin_id |
            | kokoro_v1 |

    Scenario Outline: Make a backend with custom settings
        Given I am using the <plugin_id> plugin
        When I make settings with <setting_name> set to <custom_value>
        And I make the backend using the settings
        Then the backend should use the given settings

        Examples:
            | plugin_id | setting_name | custom_value |
            | kokoro_v1 | voice        | af_bella     |

    Scenario Outline: Use a backend to convert text to speech
        Given I am using the <plugin_id> plugin
        When I make the default settings for the backend
        And I make the backend using the settings
        And I start the backend
        When I convert 'Aquarion AI is awesome!' to speech
        # Note: At the API level we are not testing for audio correctness, merely API
        #       conformance.
        Then I get a stream of binary output

        Examples:
            | plugin_id |
            | kokoro_v1 |

    Scenario Outline: Change a backend's settings
        Given I am using the <plugin_id> plugin
        When I make the default settings for the backend
        And I make the backend using the settings
        And I make new settings with <setting_name> set to <custom_value>
        And I update the backend with the new settings
        Then the backend should use the new settings

        Examples:
            | plugin_id | setting_name | custom_value |
            | kokoro_v1 | voice        | af_bella     |

    Scenario Outline: Export and import a backend's settings
        Given I am using the <plugin_id> plugin
        When I make the default settings for the backend
        And I convert the settings to a dictionary
        Then the dictionary should be convertible to JSON format
        And the dictionary should be re-importable

        Examples:
            | plugin_id |
            | kokoro_v1 |

    Scenario Outline: Get a backend's audio specification
        Given I am using the <plugin_id> plugin
        When I make the default settings for the backend
        And I make the backend using the settings
        Then the audio specification should include <format> and <sample_rate>

        Examples:
            | plugin_id | format     | sample_rate |
            | kokoro_v1 | Linear PCM | 24000       |

    Scenario Outline: Get a backend's settings specification
        Given I am using the <plugin_id> plugin
        When I get the backend's settings specification
        And I make the default settings for the backend
        Then all setting attributes should be included in the specification
        And all setting specification types should be correct

        Examples:
            | plugin_id |
            | kokoro_v1 |
