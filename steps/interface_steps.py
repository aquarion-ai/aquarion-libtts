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

"""Placeholder BDD steps."""

from radish import given, then, when
from radish.stepmodel import Step

### GIVEN ###


@given(r"I have imported the desired TTS backend class")
def given_backend_import(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@given(r"I have created a custom backend-appropriate settings object")
def given_custom_settings_object(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@given(r"I have created an invalid backend-appropriate settings object")
def given_invalid_settings_object(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@given(r"I have an instantiated TTS backend")
def given_instantiated_backend(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@given(r"I have not set custom backend-appropriate settings")
def given_default_settings(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@given(r"I have set custom backend-appropriate settings")
def given_custom_settings(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@given(r"I have some text that I want spoken")
def given_text_to_convert(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


### WHEN ###


@when(r"I call the 'create' factory class method without any settings")
def when_create_without_settings(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@when(r"I call the 'create' factory class method with the settings")
def when_create_with_settings(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@when(r"I call the 'convert' method with my text")
def when_convert_with_text(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@when(r"I access the 'settings' attribute")
def when_get_settings(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@when(r"I assign the settings object to the 'settings' attribute")
def when_set_settings(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@when(r"I call the 'reset_config' method")
def when_reset(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


### THEN ###


@then(r"I receive an instance of the backend")
def then_correct_instance(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@then(r"it has the default backend-appropriate settings applied")
def then_default_settings(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@then(r"it has the custom backend-appropriate settings applied")
def then_custom_settings(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@then(r"I receive an exception indicating that the settings are invalid")
def then_invalid_settings_exception(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@then(r"the exception includes information about which settings are invalid")
def then_invalid_settings_details(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@then(r"I receive the correct corresponding speech audio data")
def then_correct_speech_audio(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@then(r"I receive the default backend-appropriate settings object")
def then_get_default_settings(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@then(r"I receive the custom backend-appropriate settings object")
def then_get_custom_settings(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@then(r"the custom settings are applied successfully")
def then_custom_settings_applied(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)


@then(r"the default settings are applied successfully")
def then_default_settings_applied(step: Step) -> None:
    message = "This step is not implemented yet"
    raise NotImplementedError(message)
