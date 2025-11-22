"""Template YAML schema validation and loading."""

from typing import Dict, Any
from pathlib import Path
import yaml


class TemplateValidationError(Exception):
    """Raised when template YAML validation fails."""

    pass


class TemplateLoader:
    """Loads and validates template YAML files."""

    REQUIRED_FIELDS = [
        "name",
        "layer",
        "description",
        "categories",
        "rules",
        "tax_tracking",
        "alerts",
        "labels",
        "dependencies",
        "metadata",
    ]
    VALID_LAYERS = ["primary", "living", "additional"]
    LABEL_REQUIRED_FIELDS = ["name", "description", "color"]

    def load_from_string(self, yaml_content: str) -> Dict[str, Any]:
        """
        Load and validate template from YAML string.

        Args:
            yaml_content: YAML content as string

        Returns:
            Validated template dictionary

        Raises:
            TemplateValidationError: If validation fails
        """
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise TemplateValidationError(f"Invalid YAML: {e}")

        if not isinstance(data, dict):
            raise TemplateValidationError("Template must be a YAML dictionary")

        template: Dict[str, Any] = data
        self._validate_template(template)
        return template

    def load_from_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load and validate template from YAML file.

        Args:
            file_path: Path to YAML template file

        Returns:
            Validated template dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            TemplateValidationError: If validation fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")

        with open(file_path, "r") as f:
            yaml_content = f.read()

        return self.load_from_string(yaml_content)

    def _validate_template(self, template: Dict[str, Any]) -> None:
        """
        Validate template structure.

        Args:
            template: Template dictionary to validate

        Raises:
            TemplateValidationError: If validation fails
        """
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in template:
                raise TemplateValidationError(f"Missing required field: {field}")

        # Validate layer
        if template["layer"] not in self.VALID_LAYERS:
            raise TemplateValidationError(
                f"Invalid layer: {template['layer']}. Must be one of {self.VALID_LAYERS}"
            )

        # Validate categories structure
        if not isinstance(template["categories"], list):
            raise TemplateValidationError("Categories must be a list")

        # Validate rules structure
        if not isinstance(template["rules"], list):
            raise TemplateValidationError("Rules must be a list")

        # Validate alerts structure
        if not isinstance(template["alerts"], list):
            raise TemplateValidationError("Alerts must be a list")

        # Validate labels structure
        if not isinstance(template["labels"], list):
            raise TemplateValidationError("Labels must be a list")

        # Validate each label
        for label in template["labels"]:
            self._validate_label(label)

    def _validate_label(self, label: Dict[str, Any]) -> None:
        """
        Validate label structure.

        Args:
            label: Label dictionary to validate

        Raises:
            TemplateValidationError: If validation fails
        """
        # Check required fields
        for field in self.LABEL_REQUIRED_FIELDS:
            if field not in label:
                label_name = label.get("name", "unknown")
                raise TemplateValidationError(
                    f"Label missing required field: {field}. Label: {label_name}"
                )

        # Optional fields: auto_apply, requires_configuration, configuration_prompt
        # These don't need validation beyond type checking if present
        if "auto_apply" in label and not isinstance(label["auto_apply"], bool):
            raise TemplateValidationError(
                f"Label 'auto_apply' must be boolean for label: {label['name']}"
            )

        if "requires_configuration" in label and not isinstance(
            label["requires_configuration"], bool
        ):
            msg = f"Label 'requires_configuration' must be boolean for label: {label['name']}"
            raise TemplateValidationError(msg)

        if "configuration_prompt" in label and not isinstance(label["configuration_prompt"], str):
            msg = f"Label 'configuration_prompt' must be string for label: {label['name']}"
            raise TemplateValidationError(msg)
