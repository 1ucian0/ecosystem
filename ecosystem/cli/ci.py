"""CliCI class for controlling all CLI functions."""

from pathlib import Path
from ruamel.yaml import YAML
from bs4 import BeautifulSoup

from ecosystem.dao import DAO
from ecosystem.submission_parser import parse_submission_issue
from ecosystem.error_handling import set_actions_output, EcosystemError
from ecosystem.labels import LabelsToml
from ecosystem.validation import validators


class CliCI:
    """CliCI class.
    Entrypoint for all CLI CI commands.

    Each public method of this class is CLI command
    and arguments for method are options/flags for this command.

    Ex: `python manager.py ci parser_issue --body="<SOME_MARKDOWN>"`
    """

    @staticmethod
    def add_member_from_issue(body: str, *, resources_dir: str | None = None) -> None:
        """Parse an issue created from the issue template and add the member to the database

        Args:
            body: body of the created issue
            resources_dir: (For testing) Path to the working directory

        Returns:
            None (side effect is updating database and writing actions output)
        """

        resources_dir = Path(resources_dir or (Path.cwd() / "ecosystem/resources"))

        parsed_result = parse_submission_issue(body)
        DAO(path=resources_dir).write(parsed_result)
        set_actions_output([("SUBMISSION_NAME", parsed_result.name)])
        set_actions_output([("SUBMISSION_SHORT_UUID", parsed_result.short_uuid)])

    @staticmethod
    def update_issue_template(
        template_path: str, *, resources_dir: str | None = None
    ) -> None:
        """Parse an issue created from the issue template and add the member to the database

        Args:
            template_path: Path to the issue template to update
            resources_dir: Path to the resources directory
        """

        labels_toml = LabelsToml(resources_dir=resources_dir)

        yaml = YAML()
        with open(template_path, "r") as yaml_file:
            data = yaml.load(yaml_file)

        for section in data["body"]:
            if "id" not in section:
                continue
            if section["id"] == "labels":
                section["attributes"]["options"] = labels_toml.label_names
            elif section["id"] == "category":
                section["attributes"]["options"] = [
                    "Select one..."
                ] + labels_toml.category_names

        with open(template_path, "w") as yaml_file:
            yaml.dump(data, yaml_file)

    def update_validation_list(self):
        """Updates the validation list in https://qisk.it/ecosystem-checks ."""
        start_tag = "<!-- start:validation-list -->"
        end_tag = "<!-- end:validation-list -->"

        checks = []
        for validator in validators():
            lines = [
                "---",
                "",
                f'<h3 id="{validator.id}">{validator.title}</h3>',
                "",
            ]
            if validator.related_to:
                related_to_1 = " related to |"
                related_to_2 = " :---: |"
                rt = []
                for r in validator.related_to:
                    rt.append(f"[`[{r}]`](#{r})")
                related_to_3 = " ".join(rt) + "|"
            else:
                related_to_1 = ""
                related_to_2 = ""
                related_to_3 = ""
            lines += [
                "| id  | applies to | category | " + related_to_1,
                "|  :---:  | :---: | :---: | " + related_to_2,
                f"|`[{validator.id}]`| {validator.applies_to} | " + related_to_3,
                "",
                str(validator.description),
                "",
            ]
            checks.append((validator.id, "\n".join(lines)))

        checks.sort(key=lambda x: x[0])

        readme_md = Path(Path.cwd(), "ecosystem", "validation", "README.md")

        with open(readme_md, "r") as readme_file:
            content = readme_file.read()

        to_replace = content[
            content.find(start_tag) + len(start_tag) : content.rfind(end_tag)
        ]

        new_content = content.replace(to_replace, "\n".join([c[1] for c in checks]))

        soup = BeautifulSoup(new_content, "html.parser")
        ids = [tag["id"] for tag in soup.select("h3[id]")]
        duplicated_ids = [x for n, x in enumerate(ids) if x in ids[:n]]

        if duplicated_ids:
            raise EcosystemError(
                f"There are validations with duplicated id: {duplicated_ids}",
            )

        with open(readme_md, "w") as outfile:
            outfile.write(new_content)
