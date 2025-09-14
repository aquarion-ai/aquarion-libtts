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

"""Common shared BDD steps."""

from unittest import mock
from warnings import filterwarnings

from radish import after, before, given, then, when
from radish.feature import Feature
from radish.scenario import Scenario
from radish.stepmodel import Step

from aquarion.libs.libtts.api import TTSPluginRegistry


@before.each_feature
def _silence_warnings(_: Feature) -> None:
    """Silence specific warnings from dependencies."""
    filterwarnings(
        action="ignore",
        message="Importing 'parser.split_arg_string' is deprecated",
        category=DeprecationWarning,
    )
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


@after.each_scenario
def _clean_up(scenario: Scenario) -> None:
    """Make sure any started TTS backend is stopped and mocks are unpatched."""
    if hasattr(scenario.context, "backend") and scenario.context.backend.is_started:
        scenario.context.backend.stop()
    mock.patch.stopall()


### GIVENs ###


@given("I have a TTSBackendRegistry")
def _(step: Step) -> None:
    step.context.registry = TTSPluginRegistry()


@given("I have loaded all available plugins")
def _(step: Step) -> None:
    step.context.registry.load_plugins()


@given("I am using the {plugin_id:S} plugin")
@given("I am using the '{plugin_id:S}' plugin")
def _(step: Step, plugin_id: str) -> None:
    step.context.plugin_id = plugin_id
    step.context.plugin = step.context.registry.get_plugin(plugin_id)


### WHENs ###


@when("I get the display name for {locale:w}")
def _(step: Step, locale: str) -> None:
    step.context.display_name = step.context.plugin.get_display_name(locale)


@when("I make the default settings for the backend")
def _(step: Step) -> None:
    step.context.settings = step.context.plugin.make_settings()


@when("I make settings with {setting_name:w} set to {custom_value:w}")
@when("I make settings with '{setting_name:w}' set to '{custom_value:w}'")
@when("I make settings with '{setting_name:w}' set to '{custom_value:f}'")
@when("I make new settings with {setting_name:w} set to {custom_value:w}")
@when("I make new settings with '{setting_name:w}' set to '{custom_value:w}'")
@when("I make new settings with '{setting_name:w}' set to '{custom_value:f}'")
def _(step: Step, setting_name: str, custom_value: str) -> None:
    step.context.settings = step.context.plugin.make_settings(
        from_dict={setting_name: custom_value}
    )


@when("I make the backend using the settings")
def _(step: Step) -> None:
    step.context.backend = step.context.plugin.make_backend(step.context.settings)


@when("I update the backend with the new settings")
def _(step: Step) -> None:
    step.context.backend.update_settings(step.context.settings)


@when("I start the backend")
def _(step: Step) -> None:
    step.context.backend.start()


@when("I convert '{text}' to speech")
def _(step: Step, text: str) -> None:
    step.context.audio = step.context.backend.convert(text)


### THENs ###


@then("I see {display_name:QuotedString}")
def _(step: Step, display_name: str) -> None:
    assert step.context.display_name == display_name, (
        f"{step.context.display_name} does not match {display_name}"
    )


@then("the backend should use the given settings")
@then("the backend should use the new settings")
def _(step: Step) -> None:
    current_settings = step.context.backend.get_settings()
    assert current_settings == step.context.settings, (
        f"{current_settings!s} does not match {step.context.settings!s}"
    )
