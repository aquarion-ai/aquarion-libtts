"""Placeholder BDD steps."""

from radish import given, then, when
from radish.stepmodel import Step

from aquarion_tts import placeholder


@given("placeholder is imported")
def given_import(step: Step) -> None:
    pass


@when("I call placeholder")
def when_bar(step: Step) -> None:
    step.context.result = placeholder.placeholder()


@then("{text:QuotedString} is returned")
def then_bat(step: Step, text: str) -> None:
    assert step.context.result == text
