# SPDX-FileCopyrightText: 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
# SPDX-License-Identifier: CC-BY-SA-4.0

Feature: TTS Library Interface
    As a software developer
    I want to access various TTS backend implementations using a common interface
    So that the backends can be replaced in a modular or even dynamic way.

    @wip
    Scenario: Instantiation - Default Settings
        Given I have imported the desired TTS backend class
        When I call the 'create' factory class method without any settings
        Then I receive an instance of the backend
        And it has the default backend-appropriate settings applied

    @wip
    Scenario: Instantiation - Custom Settings
        Given I have imported the desired TTS backend class
        And I have created a custom backend-appropriate settings object
        When I call the 'create' factory class method with the settings
        Then I receive an instance of the backend
        And it has the custom backend-appropriate settings applied

    @wip
    Scenario: Instantiation - Invalid Settings
        Given I have imported the desired TTS backend class
        And I have created an invalid backend-appropriate settings object
        When I call the 'create' factory class method with the settings
        Then I receive an exception indicating that the settings are invalid
        And the exception includes information about which settings are invalid

    @wip
    Scenario: Text To Speech - Default Settings
        Given I have an instantiated TTS backend
        And I have not set custom backend-appropriate settings
        And I have some text that I want spoken
        When I call the 'convert' method with my text
        Then I receive the correct corresponding speech audio data

    @wip
    Scenario: Text To Speech - Custom Settings
        Given I have an instantiated TTS backend
        And I have set custom backend-appropriate settings
        And I have some text that I want spoken
        When I call the 'convert' method with my text
        Then I receive the correct corresponding speech audio data

    @wip
    Scenario: Get Default Settings
        Given I have an instantiated TTS backend
        And I have not set custom backend-appropriate settings
        When I access the 'settings' attribute
        Then I receive the default backend-appropriate settings object

    @wip
    Scenario: Get Custom Settings
        Given I have an instantiated TTS backend
        And I have set custom backend-appropriate settings
        When I access the 'settings' attribute
        Then I receive the custom backend-appropriate settings object

    @wip
    Scenario: Set Custom Settings
        Given I have an instantiated TTS backend
        And I have created a custom backend-appropriate settings object
        When I assign the settings object to the 'settings' attribute
        Then the custom settings are applied successfully

    @wip
    Scenario: Set Invalid Settings
        Given I have an instantiated TTS backend
        And I have created an invalid backend-appropriate settings object
        When I assign the settings object to the 'settings' attribute
        Then I receive an exception indicating that the settings are invalid
        And the exception includes information about which settings are invalid

    @wip
    Scenario: Reset Settings
        Given I have an instantiated TTS backend
        And I have set custom backend-appropriate settings
        When I call the 'reset_config' method
        Then the default settings are applied successfully
