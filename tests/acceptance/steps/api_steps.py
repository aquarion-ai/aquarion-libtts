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

"""API BDD steps."""

import json
from typing import Final

from radish import then, when
from radish.stepmodel import Step

MIN_AUDIO_LEN: Final = 100000  # bytes


### GIVENs ###


### WHENs ###


@when("I list all plugins IDs")
def _(step: Step) -> None:
    step.context.result = step.context.registry.list_plugin_ids(list_all=True)


@when("I enable the following plugins:")
def _(step: Step) -> None:
    step.context.enabled_plugins_table = step.table
    for row in step.table:
        step.context.registry.enable(row["plugin_id"])


@when("I disable the following plugins:")
def _(step: Step) -> None:
    step.context.disabled_plugins_table = step.table
    for row in step.table:
        step.context.registry.enable(row["plugin_id"])  # Pre-enabled
        step.context.registry.disable(row["plugin_id"])  # Explicit disable


@when("I list the plugin IDs")
def _(step: Step) -> None:
    step.context.result = step.context.registry.list_plugin_ids()


@when("I list the disabled plugin IDs")
def _(step: Step) -> None:
    step.context.result = step.context.registry.list_plugin_ids(only_disabled=True)


@when("no plugins are explicitly enabled")
def _(step: Step) -> None:
    pass  # Nothing to do


@when("I convert the settings to a dictionary")
def _(step: Step) -> None:
    step.context.settings_dict = step.context.settings.to_dict()


### THENs ###


@then("I should see the following plugin IDs:")
def _(step: Step) -> None:
    for row in step.table:
        assert row["plugin_id"] in step.context.result


@then("the plugins should be enabled")
def _(step: Step) -> None:
    for row in step.context.enabled_plugins_table:
        assert step.context.registry.is_enabled(row["plugin_id"])


@then("the plugins should be disabled")
def _(step: Step) -> None:
    for row in step.context.disabled_plugins_table:
        assert not step.context.registry.is_enabled(row["plugin_id"])


@then("I should see only the enabled plugins")
def _(step: Step) -> None:
    expected = {row["plugin_id"] for row in step.context.enabled_plugins_table}
    assert step.context.result == expected


@then("I should see the disabled plugins")
def _(step: Step) -> None:
    for row in step.context.disabled_plugins_table:
        assert row["plugin_id"] in step.context.result


@then("I should not see the enabled plugins")
def _(step: Step) -> None:
    for row in step.context.enabled_plugins_table:
        assert row["plugin_id"] not in step.context.result


@then("I should see no plugins")
def _(step: Step) -> None:
    assert step.context.result == set()


@then("I get a stream of binary output")
def _(step: Step) -> None:
    output = list(step.context.audio)
    assert all(isinstance(chunk, bytes) for chunk in output)
    assert len(b"".join(output)) > MIN_AUDIO_LEN


@then("the dictionary should be convertible to JSON format")
def _(step: Step) -> None:
    step.context.json_result = json.dumps(step.context.settings_dict)


@then("the dictionary should be re-importable")
def _(step: Step) -> None:
    imported_settings = step.context.plugin.make_settings(
        from_dict=json.loads(step.context.json_result)
    )
    assert imported_settings == step.context.settings


@then("the audio specification should include {format} and {sample_rate:d}")
def _(step: Step, format: str, sample_rate: int) -> None:  # noqa: A002
    assert step.context.backend.audio_spec.format == format
    assert step.context.backend.audio_spec.sample_rate == sample_rate
