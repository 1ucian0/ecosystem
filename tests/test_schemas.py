# This code is part of Qiskit.
#
# (C) Copyright IBM 2026.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at https://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
"""Tests for the JSON schemas in resources/"""

import json
from pathlib import Path
from unittest import TestCase

from ecosystem.classifications import ClassificationsToml


class MembersSchemaTestCase(TestCase):
    """The enums in resources/members-schema.json and the classifications should not drift"""

    def setUp(self) -> None:
        self.resources_dir = Path(__file__).parent.parent / "resources"
        with open(self.resources_dir / "members-schema.json") as schema_file:
            self.schema = json.load(schema_file)
        self.classifications = ClassificationsToml(resources_dir=self.resources_dir)

    def test_maturity_enum(self):
        """member.maturity accepts every maturity level in classifications.toml"""
        self.assertEqual(
            self.schema["properties"]["maturity"]["enum"],
            self.classifications.maturity_names,
        )

    def test_status_enum(self):
        """member.status accepts every status in classifications.toml.
        "Member" is the default status, but it can also be explicit in a member file"""
        self.assertEqual(
            self.schema["properties"]["status"]["enum"],
            self.classifications.status_names,
        )

    def test_no_items_uses_the_draft_4_array_form(self):
        """`items` has to be a schema, not a list of schemas.

        The draft-4 array form (`"items": [{...}]`) means `prefixItems` in draft
        2020-12, which the file declares. `jsonschema` rejects the whole schema over
        it, so nothing gets validated at all, while `taplo check` -- what CI runs --
        quietly drops the constraint instead and passes anything.
        """

        def walk(node, path="$"):
            if isinstance(node, dict):
                for key, value in node.items():
                    if key == "items":
                        self.assertIsInstance(
                            value,
                            dict,
                            f"{path}.items is a list; use prefixItems or a single schema",
                        )
                    walk(value, f"{path}.{key}")
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    walk(value, f"{path}[{index}]")

        walk(self.schema)
