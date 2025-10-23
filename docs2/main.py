# noqa: INP001

"""mkdocs-macros-plugin macros."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aquarion.libs.libtts.__about__ import __version__

if TYPE_CHECKING:
    from mkdocs_macros import MacrosPlugin


def define_env(env: MacrosPlugin) -> None:
    """Define variables and macros available in the templates."""
    env.variables.version = __version__
