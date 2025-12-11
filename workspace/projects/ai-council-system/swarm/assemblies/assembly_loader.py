"""
Assembly Loader - Loads assembly definitions from YAML templates

Loads and validates assembly definitions that define swarm workflows
for specific tasks.
"""

from typing import Dict, List, Optional
from pathlib import Path
from datetime import timedelta
import yaml
import logging

logger = logging.getLogger(__name__)


class AssemblyDefinition:
    """
    Represents the definition of a single assembly.

    Attributes:
        name: The name of the assembly.
        version: The version of the assembly.
        description: A description of the assembly's purpose.
        roles: A list of roles required for this assembly.
        workflow: The workflow definition for this assembly.
        success_criteria: The success criteria for this assembly.
        metadata: A dictionary for storing arbitrary metadata.
    """

    def __init__(self, data: Dict):
        """
        Initializes an AssemblyDefinition object.

        Args:
            data: A dictionary containing the assembly's data.
        """
        self.name = data.get("name", "")
        self.version = data.get("version", "1.0.0")
        self.description = data.get("description", "")
        self.roles = data.get("roles", [])
        self.workflow = data.get("workflow", {})
        self.success_criteria = data.get("success_criteria", {})
        self.metadata = data.get("metadata", {})

    def validate(self) -> tuple[bool, List[str]]:
        """
        Validates the assembly definition.

        Returns:
            A tuple containing a boolean indicating whether the definition is valid, and a list of any validation errors.
        """
        errors = []

        if not self.name:
            errors.append("Assembly must have a name")

        if not self.roles:
            errors.append("Assembly must define at least one role")

        if not self.workflow:
            errors.append("Assembly must define a workflow")

        if not self.success_criteria:
            errors.append("Assembly must define success criteria")

        # Validate workflow steps
        steps = self.workflow.get("steps", [])
        if not steps:
            errors.append("Workflow must have at least one step")

        # Check that all step roles are defined
        defined_roles = {role.get("name") for role in self.roles}
        for step in steps:
            step_role = step.get("role")
            if step_role not in defined_roles:
                errors.append(f"Step references undefined role: {step_role}")

        # Validate success criteria
        if "required_outputs" not in self.success_criteria:
            errors.append("Success criteria must define required_outputs")

        return len(errors) == 0, errors

    def get_role_names(self) -> List[str]:
        """
        Gets a list of the names of all roles in this assembly.

        Returns:
            A list of role names.
        """
        return [role.get("name") for role in self.roles]

    def get_estimated_duration(self) -> Optional[str]:
        """
        Gets the estimated duration of the assembly from its metadata.

        Returns:
            The estimated duration as a string, or None if it is not defined.
        """
        return self.metadata.get("estimated_duration")

    def get_tags(self) -> List[str]:
        """
        Gets the tags associated with the assembly from its metadata.

        Returns:
            A list of tags.
        """
        return self.metadata.get("tags", [])

    def to_dict(self) -> Dict:
        """
        Converts the AssemblyDefinition to a dictionary.

        Returns:
            A dictionary representation of the AssemblyDefinition.
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "roles": self.roles,
            "workflow": self.workflow,
            "success_criteria": self.success_criteria,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return f"AssemblyDefinition({self.name} v{self.version})"


class AssemblyLoader:
    """
    Loads and manages assembly definitions from YAML files.

    This class provides a centralized way to load, query, and manage all the
    assembly definitions for the swarm.
    """

    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initializes the AssemblyLoader.

        Args:
            templates_dir: An optional path to the directory containing the assembly templates. If not provided, a default path will be used.
        """
        self.templates_dir = templates_dir or Path(__file__).parent / "templates"
        self.assemblies: Dict[str, AssemblyDefinition] = {}
        self._load_templates()

    def _load_templates(self):
        """
        Loads all assembly templates from the templates directory.
        """
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return

        template_files = list(self.templates_dir.glob("*.yaml")) + \
                        list(self.templates_dir.glob("*.yml"))

        for template_file in template_files:
            try:
                self._load_template(template_file)
            except Exception as e:
                logger.error(f"Error loading template {template_file}: {e}")

        logger.info(f"Loaded {len(self.assemblies)} assembly templates")

    def _load_template(self, template_path: Path):
        """
        Loads a single assembly template from a YAML file.

        Args:
            template_path: The path to the template file.
        """
        try:
            with open(template_path, "r") as f:
                data = yaml.safe_load(f)

            assembly = AssemblyDefinition(data)

            # Validate assembly
            is_valid, errors = assembly.validate()
            if not is_valid:
                logger.error(
                    f"Invalid assembly {assembly.name}: {', '.join(errors)}"
                )
                return

            self.assemblies[assembly.name] = assembly
            logger.debug(f"Loaded assembly: {assembly.name}")

        except yaml.YAMLError as e:
            logger.error(f"YAML error in {template_path}: {e}")
        except Exception as e:
            logger.error(f"Error loading {template_path}: {e}")

    def get_assembly(self, name: str) -> Optional[AssemblyDefinition]:
        """
        Gets a specific assembly definition by its name.

        Args:
            name: The name of the assembly to retrieve.

        Returns:
            An AssemblyDefinition object if the assembly is found, otherwise None.
        """
        return self.assemblies.get(name)

    def get_all_assemblies(self) -> List[AssemblyDefinition]:
        """
        Gets a list of all loaded assembly definitions.

        Returns:
            A list of all AssemblyDefinition objects.
        """
        return list(self.assemblies.values())

    def get_assemblies_by_tag(self, tag: str) -> List[AssemblyDefinition]:
        """
        Gets all assemblies that have a specific tag.

        Args:
            tag: The tag to search for.

        Returns:
            A list of AssemblyDefinition objects that have the specified tag.
        """
        return [
            assembly for assembly in self.assemblies.values()
            if tag in assembly.get_tags()
        ]

    def search_assemblies(self, query: str) -> List[AssemblyDefinition]:
        """
        Searches for assemblies by name or description.

        Args:
            query: The search query.

        Returns:
            A list of AssemblyDefinition objects that match the query.
        """
        query_lower = query.lower()
        results = []

        for assembly in self.assemblies.values():
            if (
                query_lower in assembly.name.lower()
                or query_lower in assembly.description.lower()
            ):
                results.append(assembly)

        return results

    def list_assembly_names(self) -> List[str]:
        """
        Gets a list of the names of all loaded assemblies.

        Returns:
            A list of assembly names.
        """
        return list(self.assemblies.keys())

    def reload(self):
        """
        Reloads all assembly templates from the templates directory.
        """
        self.assemblies.clear()
        self._load_templates()

    def add_assembly(self, assembly: AssemblyDefinition) -> bool:
        """
        Adds or updates an assembly definition.

        Args:
            assembly: The assembly definition to add or update.

        Returns:
            True if the assembly was added successfully, False otherwise.
        """
        is_valid, errors = assembly.validate()
        if not is_valid:
            logger.error(f"Cannot add invalid assembly: {', '.join(errors)}")
            return False

        self.assemblies[assembly.name] = assembly
        logger.info(f"Added assembly: {assembly.name}")
        return True

    def remove_assembly(self, name: str) -> bool:
        """
        Removes an assembly definition.

        Args:
            name: The name of the assembly to remove.

        Returns:
            True if the assembly was removed successfully, False otherwise.
        """
        if name in self.assemblies:
            del self.assemblies[name]
            logger.info(f"Removed assembly: {name}")
            return True
        return False

    def __len__(self) -> int:
        return len(self.assemblies)

    def __contains__(self, name: str) -> bool:
        return name in self.assemblies

    def __iter__(self):
        return iter(self.assemblies.values())


# Global assembly loader instance
_assembly_loader: Optional[AssemblyLoader] = None


def get_assembly_loader() -> AssemblyLoader:
    """
    Gets the global instance of the AssemblyLoader.

    Returns:
        The global AssemblyLoader instance.
    """
    global _assembly_loader
    if _assembly_loader is None:
        _assembly_loader = AssemblyLoader()
    return _assembly_loader


def get_assembly(name: str) -> Optional[AssemblyDefinition]:
    """
    A convenience function to get an assembly definition by its name.

    Args:
        name: The name of the assembly to retrieve.

    Returns:
        An AssemblyDefinition object if the assembly is found, otherwise None.
    """
    return get_assembly_loader().get_assembly(name)


def get_all_assemblies() -> List[AssemblyDefinition]:
    """
    A convenience function to get a list of all assembly definitions.

    Returns:
        A list of all AssemblyDefinition objects.
    """
    return get_assembly_loader().get_all_assemblies()
