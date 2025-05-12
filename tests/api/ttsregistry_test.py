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


"""Unit tests for _ttsregistry."""

from copy import copy
from functools import partial
from typing import Final, TypedDict, cast

import pytest

from aquarion.libs.libtts.api._ttsbackend import ITTSBackendFactory
from aquarion.libs.libtts.api._ttsregistry import TTSRegistry, TTSRegistryRecord
from aquarion.libs.libtts.api._ttssettings import ITTSSettings, ITTSSettingsFactory
from tests.api.ttsbackend_test import dummy_make_ttsbackend
from tests.api.ttssettings_test import DummyTTSSettings, dummy_make_ttssettings

### TTSRegistryRecord Tests ###


class RegistryRecordRequiredArgumentsDict[T: ITTSSettings](TypedDict):
    """Dictionary of required arguments to for TTSRegistryRecord."""

    key: str
    display_name: str
    settings_factory: ITTSSettingsFactory[T]
    backend_factory: ITTSBackendFactory[T]


REGISTRY_RECORD_REQUIRED_ARGUMENTS: Final[
    RegistryRecordRequiredArgumentsDict[DummyTTSSettings]
] = {
    "key": "I am a key",
    "display_name": "I am a name",
    "settings_factory": dummy_make_ttssettings,
    "backend_factory": dummy_make_ttsbackend,
}
REGISTRY_RECORD_REQUIRED_ARGUMENT_NAMES = tuple(REGISTRY_RECORD_REQUIRED_ARGUMENTS)
REGISTRY_RECORD_ALTERNATE_REQUIRED_ARGUMENTS: Final[
    RegistryRecordRequiredArgumentsDict[DummyTTSSettings]
] = {
    "key": "I am a different key",
    "display_name": "I am a different name",
    "settings_factory": cast(
        "ITTSSettingsFactory[DummyTTSSettings]", partial(dummy_make_ttssettings)
    ),
    "backend_factory": cast(
        "ITTSBackendFactory[DummyTTSSettings]", partial(dummy_make_ttsbackend)
    ),
}


def test_ttsregistryrecord_should_accept_required_arguments() -> None:
    TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)


@pytest.mark.parametrize("arg_name", REGISTRY_RECORD_REQUIRED_ARGUMENT_NAMES)
def test_ttsregistryrecord_should_require_required_arguments(arg_name: str) -> None:
    required_args = REGISTRY_RECORD_REQUIRED_ARGUMENTS.copy()
    # Make only the arg under test absent.
    del required_args[arg_name]  # type: ignore [misc]
    with pytest.raises(TypeError, match="missing .* required keyword-only argument"):
        TTSRegistryRecord(**required_args)


def test_ttsregistryrecord_should_require_all_keyword_only_arguments() -> None:
    arg_values = list(REGISTRY_RECORD_REQUIRED_ARGUMENTS.values())
    with pytest.raises(
        TypeError, match="takes 1 positional argument but .* were given"
    ):
        TTSRegistryRecord(*arg_values)  # type: ignore [call-arg]


@pytest.mark.parametrize("attribute", REGISTRY_RECORD_REQUIRED_ARGUMENT_NAMES)
def test_ttsregistryrecord_should_have_all_expected_attributes(attribute: str) -> None:
    record = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    assert hasattr(record, attribute)


@pytest.mark.parametrize("attribute", REGISTRY_RECORD_REQUIRED_ARGUMENT_NAMES)
def test_ttsregistryrecord_should_use_the_given_values(attribute: str) -> None:
    record = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    expected_value = REGISTRY_RECORD_REQUIRED_ARGUMENTS[attribute]  # type: ignore [misc,literal-required]
    assert getattr(record, attribute) == expected_value  # type: ignore [misc]


@pytest.mark.parametrize("attribute", REGISTRY_RECORD_REQUIRED_ARGUMENT_NAMES)
def test_ttsregistryrecord_should_be_immutable(attribute: str) -> None:
    record = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    new_value = copy(REGISTRY_RECORD_REQUIRED_ARGUMENTS[attribute])  # type: ignore [misc,literal-required]
    with pytest.raises(AttributeError, match="cannot assign to field"):
        setattr(record, attribute, new_value)  # type: ignore [misc]


def test_ttsregistryrecord_should_equate_when_attributes_are_the_same() -> None:
    record1 = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    record2 = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    assert record1 is not record2
    assert record1 == record2


@pytest.mark.parametrize("arg_name", REGISTRY_RECORD_REQUIRED_ARGUMENT_NAMES)
def test_ttsregistryrecord_should_not_equate_when_attributes_are_different(
    arg_name: str,
) -> None:
    record1 = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    record2_args = REGISTRY_RECORD_REQUIRED_ARGUMENTS.copy()
    # Just replace one argument at a time.
    record2_args[arg_name] = REGISTRY_RECORD_ALTERNATE_REQUIRED_ARGUMENTS[arg_name]  # type: ignore [misc,literal-required]
    record2 = TTSRegistryRecord(**record2_args)
    assert record1 != record2


### TTSRegistry Tests ###

## .register() tests


def test_ttsregistry_register_should_accept_a_ttsregistryrecord_argument() -> None:
    record = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    registry = TTSRegistry()
    registry.register(record)


def test_ttsregistry_register_should_require_the_ttsregistryrecord_argument() -> None:
    registry = TTSRegistry()
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        registry.register()  # type: ignore [call-arg]


def test_ttsregistry_register_should_store_the_given_ttsregistryrecord() -> None:
    record = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    registry = TTSRegistry()
    registry.register(record)
    registry.get_record(record.key)


def test_ttsregistry_register_should_be_idempotent_for_identical_records() -> None:
    record1 = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    record2 = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    registry = TTSRegistry()
    registry.register(record1)
    registry.register(record2)
    assert registry.get_record(record2.key) is record1  # I.e. no replacement!


def test_ttsregistry_register_should_raise_error_if_key_already_used_by_another_backend(
    # (Force line wrap to fit in max line length.)
) -> None:
    record1 = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    record2_data = REGISTRY_RECORD_ALTERNATE_REQUIRED_ARGUMENTS.copy()
    record2_data["key"] = record1.key  # Make keys the same.
    record2 = TTSRegistryRecord(**record2_data)
    registry = TTSRegistry()
    registry.register(record1)
    with pytest.raises(ValueError, match="Key already in use by another TTS backend"):
        registry.register(record2)


## .get_record() tests


def test_ttsregistry_get_record_should_accept_a_key_argument() -> None:
    record = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    registry = TTSRegistry()
    registry.register(record)
    registry.get_record(record.key)


def test_ttsregistry_get_record_should_require_the_key_argument() -> None:
    registry = TTSRegistry()
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        registry.get_record()  # type: ignore [call-arg]


def test_ttsregistry_get_record_should_return_the_record_for_the_given_key() -> None:
    record = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    registry = TTSRegistry()
    registry.register(record)
    assert registry.get_record(record.key) is record


def test_ttsregistry_get_record_should_raise_an_error_if_no_record_found() -> None:
    registry = TTSRegistry()
    with pytest.raises(ValueError, match="TTS Backend not found"):
        registry.get_record("non existent key")


## .get_names() tests


def test_ttsregistry_get_names_should_accept_an_include_disabled_argument() -> None:
    registry = TTSRegistry()
    registry.get_names(include_disabled=True)


def test_ttsregistry_get_names_should_not_require_the_include_disabled_argument() -> (
    None
):
    registry = TTSRegistry()
    registry.get_names()


def test_ttsregistry_get_names_include_disabled_should_be_a_keyword_only_argument() -> (
    None
):
    registry = TTSRegistry()
    with pytest.raises(
        TypeError, match="takes 1 positional argument but .* were given"
    ):
        registry.get_names(True)  # type: ignore [misc]  # noqa: FBT003


def test_ttsregistry_get_names_should_return_an_empty_dict_if_no_records() -> None:
    registry = TTSRegistry()
    names = registry.get_names()
    assert isinstance(names, dict)
    assert not names


def test_ttsregistry_get_names_should_return_a_dict_of_keys_and_display_names() -> None:
    record1 = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    record2 = TTSRegistryRecord(**REGISTRY_RECORD_ALTERNATE_REQUIRED_ARGUMENTS)
    registry = TTSRegistry()
    registry.register(record1)
    registry.register(record2)
    registry.enable(record1.key)
    registry.enable(record2.key)
    names = registry.get_names()
    assert isinstance(names, dict)
    assert names[record1.key] == record1.display_name
    assert names[record2.key] == record2.display_name


def test_ttsregistry_get_names_should_not_include_disabled_backends_by_default() -> (
    None
):
    record1 = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    record2 = TTSRegistryRecord(**REGISTRY_RECORD_ALTERNATE_REQUIRED_ARGUMENTS)
    registry = TTSRegistry()
    registry.register(record1)
    registry.register(record2)
    registry.enable(record1.key)
    # record2 not enabled.  Disabled by default.
    names = registry.get_names()
    assert isinstance(names, dict)
    assert record1.key in names
    assert record2.key not in names


def test_ttsregistry_get_names_should_include_disabled_backends_when_requested() -> (
    None
):
    record1 = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    record2 = TTSRegistryRecord(**REGISTRY_RECORD_ALTERNATE_REQUIRED_ARGUMENTS)
    registry = TTSRegistry()
    registry.register(record1)
    registry.register(record2)
    registry.enable(record1.key)
    # record2 not enabled.  Disabled by default.
    names = registry.get_names(include_disabled=True)
    assert isinstance(names, dict)
    assert record1.key in names
    assert record2.key in names


## .enable() tests


def test_ttsregistry_enable_should_accept_a_key_argument() -> None:
    record = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    registry = TTSRegistry()
    registry.register(record)
    registry.enable(record.key)


def test_ttsregistry_enable_should_require_the_key_argument() -> None:
    registry = TTSRegistry()
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        registry.enable()  # type: ignore [call-arg]


def test_ttsregistry_enable_should_enable_the_backend() -> None:
    record = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    registry = TTSRegistry()
    registry.register(record)
    registry.enable(record.key)
    assert record.key in registry.get_names()


def test_ttsregistry_enable_should_be_idempotent() -> None:
    record = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    registry = TTSRegistry()
    registry.register(record)
    registry.enable(record.key)
    registry.enable(record.key)  # Do not go boom.
    assert record.key in registry.get_names()


def test_ttsregistry_enable_should_raise_an_error_if_key_is_not_registered() -> None:
    registry = TTSRegistry()
    with pytest.raises(ValueError, match="TTS Backend not found"):
        registry.enable("non existent key")


## .disable() tests


def test_ttsregistry_disable_should_accept_a_key_argument() -> None:
    record = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    registry = TTSRegistry()
    registry.register(record)
    registry.disable(record.key)


def test_ttsregistry_disable_should_require_the_key_argument() -> None:
    registry = TTSRegistry()
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        registry.disable()  # type: ignore [call-arg]


def test_ttsregistry_disable_should_disable_the_backend() -> None:
    record = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    registry = TTSRegistry()
    registry.register(record)
    registry.enable(record.key)
    registry.disable(record.key)
    assert record.key not in registry.get_names()


def test_ttsregistry_disable_should_be_idempotent() -> None:
    record = TTSRegistryRecord(**REGISTRY_RECORD_REQUIRED_ARGUMENTS)
    registry = TTSRegistry()
    registry.register(record)
    registry.enable(record.key)
    registry.disable(record.key)
    registry.disable(record.key)  # Do not go boom.
    assert record.key not in registry.get_names()


def test_ttsregistry_disable_should_raise_an_error_if_key_is_not_registered() -> None:
    registry = TTSRegistry()
    with pytest.raises(ValueError, match="TTS Backend not found"):
        registry.disable("non existent key")
