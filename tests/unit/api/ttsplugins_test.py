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

"""Unit tests for the .api._ttsplugins module."""

import importlib
from collections.abc import Mapping
from types import MappingProxyType
from typing import Final, Never, cast

import pytest
from logot import Logot, logged
from pluggy import PluginValidationError

from aquarion.libs.libtts.api import tts_hookimpl
from aquarion.libs.libtts.api._ttsbackend import ITTSBackend
from aquarion.libs.libtts.api._ttsplugins import (
    ITTSPlugin,
    TTSPluginRegistry,
    register_tts_plugin,
)
from aquarion.libs.libtts.api._ttssettings import (
    ITTSSettings,
    JSONSerializableTypes,
    TTSSettingsSpecEntry,
    TTSSettingsSpecEntryTypes,
)
from tests.unit.api.ttsbackend_test import DummyTTSBackend
from tests.unit.api.ttssettings_test import AnotherTTSSettings, DummyTTSSettings

### ITTSPlugin Tests ###

# These tests serve mostly to document the expectations of all ITTSPlugin
# implementations.


DUMMY_ID: Final = "I am an id"
DUMMY_DISPLAY_NAME_EN_CA: Final = "I am a display name"
DUMMY_DISPLAY_NAME_FR_CA: Final = "Je suis un nom affiché"
DUMMY_DISPLAY_NAME_DEFAULT: Final = "I am a default display name"
DUMMY_ATTR1_DISPLAY_NAME_EN_CA: Final = "I am attr1's display name"
DUMMY_ATTR1_DISPLAY_NAME_FR_CA: Final = "Je suis le nom affiché de attr1"
DUMMY_ATTR1_DISPLAY_NAME_DEFAULT: Final = "I am attr1's default display name"


class DummyTTSPlugin:
    """Dummy TTS Plugin to test the protocol.

    Specific implementations here do not matter, the only important thing is to conform
    to the ITTSPlugin protocol.
    """

    def __init__(self, id_: str = DUMMY_ID) -> None:
        self._id = id_

    @property
    def id(self) -> str:
        return self._id

    def get_display_name(self, locale: str) -> str:
        if locale == "fr_CA":
            display_name = DUMMY_DISPLAY_NAME_FR_CA
        elif locale == "en_CA":
            display_name = DUMMY_DISPLAY_NAME_EN_CA
        else:
            display_name = DUMMY_DISPLAY_NAME_DEFAULT
        return display_name

    def make_settings(
        self,
        from_dict: Mapping[str, JSONSerializableTypes] | None = None,
    ) -> ITTSSettings:
        if from_dict is None:
            settings = DummyTTSSettings()
        else:
            if "attr2" in from_dict:
                message = "Invalid setting key: [attr2]"
                raise KeyError(message)
            if from_dict["attr1"] == "invalid":
                message = f"Invalid setting value: attr1=[{from_dict['attr1']}]"
                raise ValueError(message)
            attr1 = cast("str | None", from_dict.get("attr1", None))
            settings = DummyTTSSettings(attr1=attr1)
        return settings

    def make_backend(self, settings: ITTSSettings) -> ITTSBackend:
        backend = DummyTTSBackend()
        backend.update_settings(settings)
        return backend

    def get_settings_spec(
        self,
    ) -> Mapping[str, TTSSettingsSpecEntry[TTSSettingsSpecEntryTypes]]:
        spec = {"attr1": TTSSettingsSpecEntry(type=str)}
        proxy = MappingProxyType(spec)
        return proxy  # Makes type checker happy # noqa: RET504

    def get_setting_display_name(self, setting_name: str, locale: str) -> str:
        assert setting_name == "attr1"
        if locale == "en_CA":
            return DUMMY_ATTR1_DISPLAY_NAME_EN_CA
        if locale == "fr_CA":
            return DUMMY_ATTR1_DISPLAY_NAME_FR_CA
        return DUMMY_ATTR1_DISPLAY_NAME_DEFAULT


def test_ittsplugin_should_conform_to_its_protocol() -> None:
    plugin = DummyTTSPlugin()
    _: ITTSPlugin = plugin  # Typecheck protocol conformity
    assert isinstance(plugin, ITTSPlugin)  # Runtime check as well


def test_ittsplugin_should_have_an_id_attribute() -> None:
    plugin = DummyTTSPlugin()
    assert hasattr(plugin, "id")


def test_ittsplugin_id_should_be_immutable() -> None:
    plugin = DummyTTSPlugin()
    with pytest.raises(AttributeError, match="object has no setter"):
        plugin.id = "new_id"  # type:ignore[misc]


def test_ittsplugin_id_should_have_the_correct_value() -> None:
    plugin = DummyTTSPlugin()
    assert plugin.id == DUMMY_ID


## .get_display_name test


def test_ittsplugin_get_display_name_should_accept_a_locale_argument() -> None:
    plugin = DummyTTSPlugin()
    plugin.get_display_name("en_CA")


def test_ittsplugin_get_display_name_should_require_the_locale_argument() -> None:
    plugin = DummyTTSPlugin()
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        plugin.get_display_name()  # type:ignore[call-arg]


@pytest.mark.parametrize(
    ("locale", "expected"),
    [("en_CA", DUMMY_DISPLAY_NAME_EN_CA), ("fr_CA", DUMMY_DISPLAY_NAME_FR_CA)],
)
def test_ittsplugin_get_display_name_should_return_correct_display_name_for_locale(
    locale: str, expected: str
) -> None:
    plugin = DummyTTSPlugin()
    display_name = plugin.get_display_name(locale)
    assert display_name == expected


def test_ittsplugin_get_display_name_should_return_a_fallback_if_locale_unknown() -> (
    None
):
    plugin = DummyTTSPlugin()
    display_name = plugin.get_display_name("ja")
    assert display_name == DUMMY_DISPLAY_NAME_DEFAULT


## .make_settings tests


def test_ittsplugin_make_settings_should_use_default_values_when_no_values_given() -> (
    None
):
    plugin = DummyTTSPlugin()
    settings = plugin.make_settings()
    assert isinstance(settings, DummyTTSSettings)  # For the type checker
    assert settings.attr1 == "default"


def test_ittsplugin_make_settings_should_use_given_values_when_values_are_given() -> (
    None
):
    plugin = DummyTTSPlugin()
    settings = plugin.make_settings(from_dict={"attr1": "custom"})
    assert isinstance(settings, DummyTTSSettings)  # For the type checker
    assert settings.attr1 == "custom"


def test_ittsplugin_make_settings_should_return_a_ittssettings_object() -> None:
    plugin = DummyTTSPlugin()
    settings = plugin.make_settings()
    _: ITTSSettings = settings  # Typecheck protocol conformity
    assert isinstance(settings, ITTSSettings)  # Runtime check as well


def test_ittsplugin_make_settings_should_raise_an_error_if_an_invalid_key_given() -> (
    None
):
    plugin = DummyTTSPlugin()
    with pytest.raises(KeyError, match="Invalid setting key"):
        plugin.make_settings(from_dict={"attr2": "invalid"})


def test_ittsplugin_make_settings_should_raise_an_error_if_an_invalid_value_given() -> (
    None
):
    plugin = DummyTTSPlugin()
    with pytest.raises(ValueError, match="Invalid setting value"):
        plugin.make_settings(from_dict={"attr1": "invalid"})


## .make_backend tests


def test_ittsplugin_make_backend_should_require_a_settings_argument() -> None:
    plugin = DummyTTSPlugin()
    with pytest.raises(TypeError, match="missing *. required positional argument"):
        plugin.make_backend()  # type:ignore[call-arg]


def test_ittsplugin_make_backend_should_use_the_given_settings() -> None:
    expected = "custom"
    plugin = DummyTTSPlugin()
    backend = plugin.make_backend(DummyTTSSettings(expected))
    settings = backend.get_settings()
    assert isinstance(settings, DummyTTSSettings)  # For the type checker
    assert settings.attr1 == expected


def test_ittsplugin_make_backend_should_return_a_ittsbackend_object() -> None:
    plugin = DummyTTSPlugin()
    settings = DummyTTSSettings()
    backend = plugin.make_backend(settings)
    _: ITTSBackend = backend  # Typecheck protocol conformity
    assert isinstance(backend, ITTSBackend)  # Runtime check as well


def test_ittsplugin_make_backend_should_raise_error_if_incorrect_settings_given() -> (
    None
):
    plugin = DummyTTSPlugin()
    settings = AnotherTTSSettings()
    with pytest.raises(TypeError, match="Incorrect settings type"):
        plugin.make_backend(settings)


## .get_settings_spec tests


def test_ittsplugin_get_settings_spec_should_return_a_mapping_of_ttssettingsspecentry(
    # Force line wrap in Ruff.
) -> None:
    plugin = DummyTTSPlugin()
    spec = plugin.get_settings_spec()
    assert isinstance(spec, Mapping)
    assert all(isinstance(entry, TTSSettingsSpecEntry) for entry in spec.values())


def test_ittsplugin_get_settings_spec_result_should_include_all_settings() -> None:
    plugin = DummyTTSPlugin()
    spec = plugin.get_settings_spec()
    assert set(spec.keys()) == {"attr1"}


def test_ittsplugin_get_settings_spec_result_should_be_immutable() -> None:
    plugin = DummyTTSPlugin()
    spec = plugin.get_settings_spec()
    with pytest.raises(TypeError, match="object does not support item assignment"):
        spec["new_key"] = "invalid"  # type:ignore[index]
    with pytest.raises(TypeError, match="object does not support item assignment"):
        spec["attr1"] = "also invalid"  # type:ignore[index]


## .get_setting_display_name tests


GET_SETTING_DISPLAY_NAME_ARGS: Final = {
    "setting_name": "attr1",
    "locale": "en_CA",
}


def test_ittsplugin_get_setting_display_name_should_accept_required_arguments() -> None:
    plugin = DummyTTSPlugin()
    plugin.get_setting_display_name(**GET_SETTING_DISPLAY_NAME_ARGS)


@pytest.mark.parametrize("argument", GET_SETTING_DISPLAY_NAME_ARGS)
def test_ittsplugin_get_setting_display_name_should_require_required_arguments(
    argument: str,
) -> None:
    args = GET_SETTING_DISPLAY_NAME_ARGS.copy()
    del args[argument]
    plugin = DummyTTSPlugin()
    with pytest.raises(TypeError, match="missing 1 required positional argument"):
        plugin.get_setting_display_name(**args)


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("en_CA", DUMMY_ATTR1_DISPLAY_NAME_EN_CA),
        ("fr_CA", DUMMY_ATTR1_DISPLAY_NAME_FR_CA),
    ],
)
def test_ittsplugin_get_setting_display_name_should_return_correct_name_for_locale(
    locale: str, expected: str
) -> None:
    plugin = DummyTTSPlugin()
    display_name = plugin.get_setting_display_name("attr1", locale)
    assert display_name == expected


def test_ittsplugin_get_setting_display_name_should_return_a_fallback_if_locale_unknown(
    # Force line wrap in Ruff.
) -> None:
    plugin = DummyTTSPlugin()
    display_name = plugin.get_setting_display_name("attr1", "ja")
    assert display_name == DUMMY_ATTR1_DISPLAY_NAME_DEFAULT


### TTSPluginRegistry Tests ###


class DummyNamespace:
    """Dummy namespace (fake module) for our dummy hook implementation."""

    @tts_hookimpl
    def register_tts_plugin(self) -> ITTSPlugin | None:
        return DummyTTSPlugin()

    @tts_hookimpl
    def invalid_hook(self) -> Never:
        message = "This should never run"  # pragma: no cover
        raise NotImplementedError(message)  # pragma: no cover

    @tts_hookimpl(specname="register_tts_plugin")  # type:ignore[misc]
    def skip_me(self) -> ITTSPlugin | None:
        return None


class DummyEntryPoint:
    """Dummy entry point for plugin loading."""

    name = "dummy"
    group = tts_hookimpl.project_name
    value = "dummy:dummy"

    def load(self) -> DummyNamespace:
        return DummyNamespace()


class Distribution:
    """Dummy distribution containing out dummy entry point."""

    entry_points = (DummyEntryPoint(),)


def dummy_distributions() -> tuple[Distribution, ...]:
    return (Distribution(),)


@pytest.fixture  # type:ignore[misc]
def configured_registry() -> tuple[TTSPluginRegistry, list[str]]:
    """Return a TTSPluginRegistry and ids for some pre-configured dummy plugins."""
    registry = TTSPluginRegistry()
    plugin1 = DummyTTSPlugin("plugin1")  # Default disabled
    plugin2 = DummyTTSPlugin("plugin2")
    plugin3 = DummyTTSPlugin("plugin3")
    registry._register_test_plugin(plugin1)  # noqa: SLF001
    registry._register_test_plugin(plugin2)  # noqa: SLF001
    registry._register_test_plugin(plugin3)  # noqa: SLF001
    registry.enable(plugin2.id)  # Explicitly enabled
    registry.enable(plugin3.id)
    registry.disable(plugin3.id)  # Explicitly disabled
    return registry, [plugin1.id, plugin2.id, plugin3.id]


## .load_plugins tests

# Based on: https://github.com/pytest-dev/pluggy/blob/main/testing/test_pluginmanager.py


def test_ttspluginregistry_load_plugins_should_accept_optional_validate_argument(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(importlib.metadata, "distributions", dummy_distributions)
    registry = TTSPluginRegistry()
    registry.load_plugins(validate=False)


def test_ttspluginregistry_load_plugins_should_require_validate_to_be_keyword_only(
    # Force line wrap in Ruff.
) -> None:
    registry = TTSPluginRegistry()
    with pytest.raises(
        TypeError, match="takes .* positional argument.? but .* were given"
    ):
        registry.load_plugins(False)  # type:ignore[misc]  # noqa: FBT003


def test_ttspluginregistry_load_plugins_should_load_plugins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(importlib.metadata, "distributions", dummy_distributions)
    registry = TTSPluginRegistry()
    registry.load_plugins(validate=False)
    assert registry.get_plugin("I am an id")


def test_ttspluginregistry_load_plugins_should_raise_error_if_invalid_hookimpl(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(importlib.metadata, "distributions", dummy_distributions)
    registry = TTSPluginRegistry()
    with pytest.raises(PluginValidationError, match="unknown hook .* in plugin"):
        registry.load_plugins()


def test_ttspluginregistry_load_plugins_should_not_raise_error_if_validate_is_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(importlib.metadata, "distributions", dummy_distributions)
    registry = TTSPluginRegistry()
    registry.load_plugins(validate=False)


def test_ttspluginregistry_load_plugins_should_raise_error_if_no_plugins_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(importlib.metadata, "distributions", lambda: ())
    registry = TTSPluginRegistry()
    with pytest.raises(RuntimeError, match="No TTS plugins were found"):
        registry.load_plugins()


def test_ttspluginregistry_load_plugins_should_log_the_loading_of_plugins(
    monkeypatch: pytest.MonkeyPatch, logot: Logot
) -> None:
    monkeypatch.setattr(importlib.metadata, "distributions", dummy_distributions)
    registry = TTSPluginRegistry()
    registry.load_plugins(validate=False)
    logot.assert_logged(
        logged.debug("Loading TTS plugins for %s...")
        >> logged.debug("Registered TTS plugin: I am an id")
        >> logged.debug("Total TTS plugins registered: 1")
    )


def test_ttspluginregistry_load_plugins_should_let_hooks_be_skipped_by_returning_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(importlib.metadata, "distributions", dummy_distributions)
    registry = TTSPluginRegistry()
    registry.load_plugins(validate=False)
    with pytest.raises(ValueError, match="TTS plugin not found"):
        registry.get_plugin("I should be skipped")


@pytest.mark.parametrize("plugin_id", ["kokoro_v1"])
def test_ttspluginregistry_load_plugins_should_load_builtin_plugins(
    plugin_id: str,
) -> None:
    registry = TTSPluginRegistry()
    registry.load_plugins(validate=True)
    plugin = registry.get_plugin(plugin_id)
    assert isinstance(plugin, ITTSPlugin)


## .list_plugin_ids() tests


def test_ttspluginregistry_list_plugin_ids_should_accept_only_disabled_argument() -> (
    None
):
    registry = TTSPluginRegistry()
    registry.list_plugin_ids(only_disabled=True)


def test_ttspluginregistry_list_plugin_ids_should_accept_a_list_all_argument() -> None:
    registry = TTSPluginRegistry()
    registry.list_plugin_ids(list_all=True)


def test_ttspluginregistry_list_plugin_ids_should_only_accept_keyword_arguments() -> (
    None
):
    registry = TTSPluginRegistry()
    with pytest.raises(
        TypeError, match="takes 1 positional argument but .* were given"
    ):
        registry.list_plugin_ids(False, False)  # type:ignore[misc]  # noqa: FBT003


def test_ttspluginregistry_list_plugin_ids_should_return_enabled_plugin_ids_by_default(
    configured_registry: tuple[TTSPluginRegistry, list[str]],
) -> None:
    registry, ids = configured_registry
    plugin_ids = registry.list_plugin_ids()
    assert plugin_ids == {ids[1]}


def test_ttspluginregistry_list_plugin_ids_should_return_disabled_plugin_ids(
    configured_registry: tuple[TTSPluginRegistry, list[str]],
) -> None:
    registry, ids = configured_registry
    plugin_ids = registry.list_plugin_ids(only_disabled=True)
    assert plugin_ids == {ids[0], ids[2]}


def test_ttspluginregistry_list_plugin_ids_should_return_all_plugin_ids(
    configured_registry: tuple[TTSPluginRegistry, list[str]],
) -> None:
    registry, ids = configured_registry
    plugin_ids = registry.list_plugin_ids(list_all=True)
    assert plugin_ids == set(ids)


def test_ttspluginregistry_list_plugin_ids_should_raise_error_if_invalid_args_combo(
    # Force line wrap in Ruff.
) -> None:
    registry = TTSPluginRegistry()
    with pytest.raises(ValueError, match="Invalid argument combination"):
        registry.list_plugin_ids(only_disabled=True, list_all=True)


## .get_plugin() tests


def test_ttspluginregistry_get_plugin_should_accept_an_id_argument() -> None:
    registry = TTSPluginRegistry()
    plugin = DummyTTSPlugin()
    registry._register_test_plugin(plugin)  # noqa: SLF001
    registry.get_plugin(plugin.id)


def test_ttspluginregistry_get_plugin_should_require_the_id_argument() -> None:
    registry = TTSPluginRegistry()
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        registry.get_plugin()  # type:ignore[call-arg]


def test_ttspluginregistry_get_plugin_should_return_the_plugin_for_the_given_id() -> (
    None
):
    registry = TTSPluginRegistry()
    plugin = DummyTTSPlugin()
    registry._register_test_plugin(plugin)  # noqa: SLF001
    assert registry.get_plugin(plugin.id) is plugin


def test_ttspluginregistry_get_plugin_should_raise_an_error_if_no_record_found() -> (
    None
):
    registry = TTSPluginRegistry()
    with pytest.raises(ValueError, match="TTS plugin not found"):
        registry.get_plugin("non existent if")


## .is_enabled() tests


def test_ttspluginregistry_is_enabled_should_return_true_if_plugin_is_enabled() -> None:
    plugin = DummyTTSPlugin()
    registry = TTSPluginRegistry()
    registry._register_test_plugin(plugin)  # noqa: SLF001
    registry.enable(plugin.id)
    assert registry.is_enabled(plugin.id)


def test_ttspluginregistry_is_enabled_should_return_false_if_plugin_is_disabled() -> (
    None
):
    plugin = DummyTTSPlugin()
    registry = TTSPluginRegistry()
    registry._register_test_plugin(plugin)  # noqa: SLF001
    registry.enable(plugin.id)
    registry.disable(plugin.id)
    assert not registry.is_enabled(plugin.id)


## .enable() tests


def test_ttspluginregistry_enable_should_accept_an_id_argument() -> None:
    plugin = DummyTTSPlugin()
    registry = TTSPluginRegistry()
    registry._register_test_plugin(plugin)  # noqa: SLF001
    registry.enable(plugin.id)


def test_ttspluginregistry_enable_should_require_the_id_argument() -> None:
    registry = TTSPluginRegistry()
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        registry.enable()  # type:ignore[call-arg]


def test_ttspluginregistry_enable_should_enable_the_plugin() -> None:
    registry = TTSPluginRegistry()
    plugin = DummyTTSPlugin()
    registry._register_test_plugin(plugin)  # noqa: SLF001
    registry.enable(plugin.id)
    assert registry.is_enabled(plugin.id)


def test_ttspluginregistry_enable_should_be_idempotent() -> None:
    registry = TTSPluginRegistry()
    plugin = DummyTTSPlugin()
    registry._register_test_plugin(plugin)  # noqa: SLF001
    registry.enable(plugin.id)
    registry.enable(plugin.id)  # Do not go boom.
    assert registry.is_enabled(plugin.id)


def test_ttspluginregistry_enable_should_raise_an_error_if_id_is_not_registered() -> (
    None
):
    registry = TTSPluginRegistry()
    with pytest.raises(ValueError, match="TTS plugin not found"):
        registry.enable("non existent id")


def test_ttspluginregistry_enable_should_log_the_enablement(logot: Logot) -> None:
    plugin = DummyTTSPlugin()
    registry = TTSPluginRegistry()
    registry._register_test_plugin(plugin)  # noqa: SLF001
    registry.enable(plugin.id)
    logot.assert_logged(logged.debug(f"Enabled TTS plugin: {plugin.id}"))


## .disable() tests


def test_ttspluginregistry_disable_should_accept_an_id_argument() -> None:
    plugin = DummyTTSPlugin()
    registry = TTSPluginRegistry()
    registry._register_test_plugin(plugin)  # noqa: SLF001
    registry.disable(plugin.id)


def test_ttspluginregistry_disable_should_require_the_id_argument() -> None:
    registry = TTSPluginRegistry()
    with pytest.raises(TypeError, match="missing .* required positional argument"):
        registry.disable()  # type:ignore[call-arg]


def test_ttspluginregistry_disable_should_disable_the_plugin() -> None:
    registry = TTSPluginRegistry()
    plugin = DummyTTSPlugin()
    registry._register_test_plugin(plugin)  # noqa: SLF001
    registry.enable(plugin.id)
    registry.disable(plugin.id)
    assert not registry.is_enabled(plugin.id)


def test_ttspluginregistry_disable_should_be_idempotent() -> None:
    registry = TTSPluginRegistry()
    plugin = DummyTTSPlugin()
    registry._register_test_plugin(plugin)  # noqa: SLF001
    registry.enable(plugin.id)
    registry.disable(plugin.id)
    registry.disable(plugin.id)  # Do not go boom.
    assert not registry.is_enabled(plugin.id)


def test_ttspluginregistry_disable_should_raise_an_error_if_id_is_not_registered() -> (
    None
):
    registry = TTSPluginRegistry()
    with pytest.raises(ValueError, match="TTS plugin not found"):
        registry.disable("non existent id")


def test_ttspluginregistry_disable_should_log_the_disablement(logot: Logot) -> None:
    plugin = DummyTTSPlugin()
    registry = TTSPluginRegistry()
    registry._register_test_plugin(plugin)  # noqa: SLF001
    registry.enable(plugin.id)
    registry.disable(plugin.id)
    logot.assert_logged(logged.debug(f"Disabled TTS plugin: {plugin.id}"))


### register_tts_plugin spec Tests ###

# These tests serve mostly to document the expectations of all ITTSPlugin
# implementations.


@tts_hookimpl(specname="register_tts_plugin")  # type:ignore[misc]
def dummy_register_tts_plugin() -> ITTSPlugin:
    return DummyTTSPlugin()


def test_register_tts_plugin_should_be_a_hookspec() -> None:
    assert hasattr(register_tts_plugin, "aquarion-libtts_spec")


def test_register_tts_plugin_should_return_an_ittsplugin() -> None:
    plugin = dummy_register_tts_plugin()
    _: ITTSPlugin = plugin  # Typecheck protocol conformity
    assert isinstance(plugin, ITTSPlugin)  # Runtime check as well
