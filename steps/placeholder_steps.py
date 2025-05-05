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

from aquarion.libs.libtts import placeholder


@given("placeholder is imported")
def given_import(step: Step) -> None:
    pass


@when("I call placeholder")
def when_bar(step: Step) -> None:
    step.context.result = placeholder.placeholder()


@then("{text:QuotedString} is returned")
def then_bat(step: Step, text: str) -> None:
    assert step.context.result == text
