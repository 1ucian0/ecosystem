"""Validation module"""

from ecosystem.error_handling import logger
from .base import MemberValidator
from .labels import *

# pylint: disable=pointless-string-statement

"""  
TODO json:
 - check no member repetition
 - check against schema
TODO member:
 - check license unification naming
 - check that is has a category (or Other, otherwise)
 - if label "research" check if there is a paper
 - if cannot be fixed, collect an "issues" property in the member toml
 - check description length
 - check "website" is not the github repo or similar
"""


def _all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in _all_subclasses(c)]
    )


def validators():
    """Generator of Validator instances"""
    for subclass in _all_subclasses(MemberValidator):
        sc = subclass()
        if (
            sc.id is None
            and sc.category is None
            and not sc.validator_class.startswith("Test")
        ):
            continue
        yield sc


def validate_member(member):
    """Runs all the validation for a member"""
    results = []
    for validator in validators():
        try:
            validator.validate(member)
        except NotImplementedError:
            logger.error(
                "the validation %s does not implement the method test",
                validator.validator_class,
            )
        except AssertionError as assertion:
            logger.error(str(assertion))
        results.append(validator)
    return results
