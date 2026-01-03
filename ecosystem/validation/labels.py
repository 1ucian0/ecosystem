"""Validations involving ecosystem/resources/labels.toml"""

from os import path
from pathlib import Path
import tomllib

from .base import MemberValidator


class LoadTOMLLabels(MemberValidator):
    # pylint: disable=invalid-name, abstract-method)
    """Base class that loads ecosystem/resources/labels.toml"""

    def __init__(self):
        super().__init__()
        dir_path = path.dirname(path.realpath(__file__))
        labels_toml = path.abspath(Path(dir_path, "..", "resources", "labels.toml"))
        with open(labels_toml, "rb") as f:
            data = tomllib.load(f)
        self.categories = [c["name"] for c in data["categories"]]
        self.labels = [c["name"] for c in data["labels"]]


class TestCategoryExists(MemberValidator):
    """
    The entry `member.group` should exist for all the members.
    """

    id = "C09"
    category = "METADATA"
    affects = "group"
    title = "All members should a category in the <code>group</code> entry"

    def test(self):
        self.assertIsNotNoneOrEmpty(
            self.member.group,
            "members should have a category/group."
            "See the list of possible categories in https://github"
            ".com/Qiskit/ecosystem/blob/main/ecosystem/resources"
            "/labels.toml",
        )


class TestCategory(LoadTOMLLabels):
    """
    The category defined by `member.group` should a valid category.
    See the possible list of categories and their
    description
    [here](https://github.com/Qiskit/ecosystem/blob/main/ecosystem/resources/labels.toml)
    """

    id = "C10"
    category = "METADATA"
    affects = "group"
    title = "Member's category should be valid"

    def test(self):
        self.assertIn(
            self.member.group,
            self.categories,
            "`{}` is not a valid category",
            self.member.group,
        )


class TestLabelExists(MemberValidator):
    """
    The entry `member.labels` should exist for all the members and have,
    at least one label in the list.
    """

    title = "Members should have, at least, one label"
    id = "L09"
    category = "METADATA"
    affects = "labels"

    def test(self):
        self.assertIsNotNoneOrEmpty(
            self.member.labels,
            "members should have, at least, one label. "
            "See the list of possible labels in https://github"
            ".com/Qiskit/ecosystem/blob/main/ecosystem/resources"
            "/labels.toml",
        )


class TestLabel(LoadTOMLLabels):
    """
    All the labels in `member.labels` should exist in the list of labels defined
    [here](https://github.com/Qiskit/ecosystem/blob/main/ecosystem/resources/labels.toml).
    """

    id = "L10"
    category = "METADATA"
    title = "All the labels for a member should be valid"

    def test(self):
        self.assertSubset(
            self.member.labels,
            self.labels,
            msg="One or more of the labels for this member are not valid. "
            "See the list of possible labels in https://github"
            ".com/Qiskit/ecosystem/blob/main/ecosystem/resources"
            "/labels.toml",
        )
