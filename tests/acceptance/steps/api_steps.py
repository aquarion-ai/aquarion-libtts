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

from __future__ import annotations

import builtins
import json
import pathlib
import types
import typing
from enum import EnumType
from pathlib import Path
from types import NoneType, UnionType
from typing import Annotated, Any, Final, Optional, get_args, get_origin

from radish import then, when

if typing.TYPE_CHECKING:
    from radish.stepmodel import Step

    from aquarion.libs.libtts.api import TTSSettingsSpecEntryTypes, TTSSettingsSpecType

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


@when("I get the display name for {locale:w}")
def _(step: Step, locale: str) -> None:
    step.context.display_name = step.context.plugin.get_display_name(locale)


@when("I convert the settings to a dictionary")
def _(step: Step) -> None:
    step.context.settings_dict = step.context.settings.to_dict()


@when("I get the backend's settings specification")
def _(step: Step) -> None:
    step.context.spec = step.context.plugin.get_settings_spec()


@when("I get the display name for {setting_name:w} for {locale:w}")
def _(step: Step, setting_name: str, locale: str) -> None:
    step.context.display_name = step.context.plugin.get_setting_display_name(
        setting_name, locale
    )


@when("I get the description for {setting_name:w} for {locale:w}")
def _(step: Step, setting_name: str, locale: str) -> None:
    step.context.description = step.context.plugin.get_setting_description(
        setting_name, locale
    )


@when("I get the supported locales")
def _(step: Step) -> None:
    step.context.supported_locales = step.context.plugin.get_supported_locales()


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


@then("I see the display name is {display_name:QuotedString}")
def _(step: Step, display_name: str) -> None:
    assert step.context.display_name == display_name, (
        f"{step.context.display_name} does not match {display_name}"
    )


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


@then("all setting attributes should be included in the specification")
def _(step: Step) -> None:
    for setting_name in step.context.settings.__dataclass_fields__:
        assert setting_name in step.context.spec, f"{setting_name} not in specification"


@then("all setting specification types should be correct")
def _(step: Step) -> None:
    spec = step.context.spec
    for setting_name, field in step.context.settings.__pydantic_fields__.items():
        assert_settings_spec_types(setting_name, spec, field.annotation)


@then("I see the description starts with {description:QuotedString}")
def _(step: Step, description: str) -> None:
    assert step.context.description.startswith(description), (
        f"{step.context.description} does not match {description}"
    )


@then("I see that {locale:w} is included")
def _(step: Step, locale: str) -> None:
    assert locale in step.context.supported_locales


### Utility Functions ###


def assert_settings_spec_types(
    setting_name: str,
    spec: TTSSettingsSpecType,
    setting_type: Any,  # noqa: ANN401
) -> None:
    """Check that settings types match their spec type.

    This is a recursive function.

    """
    concrete_type = get_origin(setting_type)
    if concrete_type is None:
        concrete_type = setting_type
    match concrete_type:
        case builtins.str | builtins.int | builtins.float:
            assert_base_spec_type(setting_name, spec, setting_type)
        case EnumType() as enum_type:
            assert_enum_spec_type(setting_name, spec, enum_type)
        case pathlib.Path:
            assert_path_spec_type(setting_name, spec, setting_type)
        case types.UnionType | typing.Union if NoneType in get_args(setting_type):
            # Note: Optional[X] is an alias for Union[X, None], so both forms are caught
            # here.
            nested_type = assert_union_with_none_setting_type(
                setting_name, setting_type
            )
            assert_settings_spec_types(setting_name, spec, nested_type)
        case typing.Annotated:
            nested_type = unwrap_annotated_setting_type(setting_type)
            assert_settings_spec_types(setting_name, spec, nested_type)
        case _:
            message = (
                f"Setting type {setting_type} is unsupported for settings spec testing"
                f" for setting {setting_name}"
            )
            raise AssertionError(message)


def assert_base_spec_type(
    setting_name: str,
    spec: TTSSettingsSpecType,
    setting_type: TTSSettingsSpecEntryTypes,
) -> None:
    """Assert that the spec type and the setting base type match."""
    spec_type = spec[setting_name].type
    assert spec_type is setting_type, (
        f"Spec type {spec_type} does not match setting type {setting_type} for setting "
        f"{setting_name}"
    )


def assert_enum_spec_type(
    setting_name: str, spec: TTSSettingsSpecType, setting_type: EnumType
) -> None:
    """Assert that the spec values and type match the enum options and value types."""
    spec_type = spec[setting_name].type
    spec_values = spec[setting_name].values
    assert len(spec_values) > 0, (
        f"Spec missing valid values for setting {setting_name} of type {setting_type}"
    )
    assert len(spec_values) == len(setting_type), (
        f"Spec values {spec_values} and enum {setting_type} values do not "
        f"match for setting {setting_name}"
    )
    for enum_entry in setting_type:
        enum_value_type = type(enum_entry.value)
        assert enum_value_type is spec_type, (
            f"Spec type {spec_type} does not match enum value type {enum_value_type}"
        )


def assert_path_spec_type(
    setting_name: str,
    spec: TTSSettingsSpecType,
    setting_type: Path,
) -> None:
    """Assert that Path setting types are treated as str spec types."""
    spec_type = spec[setting_name].type
    is_correct = setting_type is Path and spec_type is str
    assert is_correct, (
        f"Spec type {spec_type} is incorrect for setting type {setting_type} for "
        f"setting {setting_name}"
    )


def assert_union_with_none_setting_type(
    setting_name: str,
    setting_type: UnionType | Optional[Any],  # noqa: ANN401, UP045
) -> Any:  # noqa: ANN401
    """Assert that the setting type matches 'Nested | None' and return Nested."""
    union_args = set(get_args(setting_type))
    assert len(union_args) == 2, (
        f"Too many possibilities in {setting_type} for settings {setting_name}"
    )
    assert NoneType in union_args, (
        f"Union {setting_type} does not include None for setting {setting_name}"
    )
    union_args.remove(NoneType)
    return union_args.pop()


def unwrap_annotated_setting_type(setting_type: Annotated[Any, Any]) -> Any:  # noqa: ANN401
    """Return the nested type from an Annotated type hint."""
    return next(iter(get_args(setting_type)))
