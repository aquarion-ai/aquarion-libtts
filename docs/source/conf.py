# SPDX-FileCopyrightText: 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>  # noqa: INP001
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

"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

"""

import os

from aquarion.libs.libtts.__about__ import __version__

os.environ["SPHINX_BUILD"] = "1"  # Enable code to detect when imported by Sphinx.

# -- Sphinx ----------------------------------------------------------------------------

project = "aquarion-libtts"
copyright = "2025-present, Krys Lawrence"  # noqa: A001
author = "Krys Lawrence"

release = f"v{__version__}"
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "myst_parser",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = []

language = "en"

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Autosummary -----------------------------------------------------------------------

autosummary_ignore_module_all = False
autosummary_generate_overwrite = True

# -- Autodoc ---------------------------------------------------------------------------

autodoc_default_options = {
    "members": True,
    "inherited-members": True,
    "show-inheritance": True,
    "class-doc-from": "both",
    "undoc-members": True,
}

# -- Napoleon --------------------------------------------------------------------------


# -- Read The Docs Theme ---------------------------------------------------------------

html_theme_options = {
    "prev_next_buttons_location": "both",
    "style_external_links": True,
}

# -- Myst Parser -----------------------------------------------------------------------

myst_enable_extensions = [
    "substitution",
    "colon_fence",
    "replacements",
    "smartquotes",
    "deflist",
]
myst_substitutions = {
    "release": release,
    "version": version,
}
myst_heading_anchors = 2

# -- Intersphinx -----------------------------------------------------------------------

intersphinx_mapping = {"python": ("https://docs.python.org/3.12", None)}
