"""
Role Loader - Loads and manages role definitions

Loads role definitions from YAML and provides utilities for
role management and validation.
"""

from typing import Dict, List, Optional
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)


class RoleDefinition:
    """
    Represents the definition of a single role.

    Attributes:
        role_id: The unique identifier for the role.
        name: The display name of the role.
        description: A description of the role's purpose.
        capabilities: A list of capabilities required for this role.
        responsibilities: A list of responsibilities for this role.
        dependencies: A list of other roles that this role depends on.
        skills_required: A list of skills required for this role.
        output_artifacts: A list of artifacts that this role is expected to produce.
    """

    def __init__(self, role_id: str, data: Dict):
        """
        Initializes a RoleDefinition object.

        Args:
            role_id: The unique identifier for the role.
            data: A dictionary containing the role's data.
        """
        self.role_id = role_id
        self.name = data.get("name", role_id)
        self.description = data.get("description", "")
        self.capabilities = data.get("capabilities", [])
        self.responsibilities = data.get("responsibilities", [])
        self.dependencies = data.get("dependencies", [])
        self.skills_required = data.get("skills_required", [])
        self.output_artifacts = data.get("output_artifacts", [])

    def has_capability(self, capability: str) -> bool:
        """
        Checks if the role requires a specific capability.

        Args:
            capability: The name of the capability to check for.

        Returns:
            True if the role requires the capability, False otherwise.
        """
        return capability in self.capabilities

    def has_all_capabilities(self, capabilities: List[str]) -> bool:
        """
        Checks if the role requires all of a given list of capabilities.

        Args:
            capabilities: A list of capability names to check for.

        Returns:
            True if the role requires all of the specified capabilities, False otherwise.
        """
        return all(cap in self.capabilities for cap in capabilities)

    def has_any_capability(self, capabilities: List[str]) -> bool:
        """
        Checks if the role requires at least one of a given list of capabilities.

        Args:
            capabilities: A list of capability names to check for.

        Returns:
            True if the role requires at least one of the specified capabilities, False otherwise.
        """
        return any(cap in self.capabilities for cap in capabilities)

    def to_dict(self) -> Dict:
        """
        Converts the RoleDefinition to a dictionary.

        Returns:
            A dictionary representation of the RoleDefinition.
        """
        return {
            "role_id": self.role_id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "responsibilities": self.responsibilities,
            "dependencies": self.dependencies,
            "skills_required": self.skills_required,
            "output_artifacts": self.output_artifacts,
        }

    def __repr__(self) -> str:
        return f"RoleDefinition({self.role_id}: {self.name})"


class RoleLoader:
    """
    Loads and manages role definitions from YAML files.

    This class provides a centralized way to load, query, and manage all the
    role definitions for the swarm.
    """

    def __init__(self, definitions_path: Optional[Path] = None):
        """
        Initializes the RoleLoader.

        Args:
            definitions_path: An optional path to the role definitions YAML file. If not provided, a default path will be used.
        """
        self.definitions_path = definitions_path or Path(__file__).parent / "role_definitions.yaml"
        self.roles: Dict[str, RoleDefinition] = {}
        self.categories: Dict[str, List[str]] = {}
        self._load_definitions()

    def _load_definitions(self):
        """
        Loads the role definitions from the YAML file.
        """
        try:
            with open(self.definitions_path, "r") as f:
                data = yaml.safe_load(f)

            # Load roles
            roles_data = data.get("roles", {})
            for role_id, role_data in roles_data.items():
                self.roles[role_id] = RoleDefinition(role_id, role_data)

            # Load categories
            self.categories = data.get("categories", {})

            logger.info(
                f"Loaded {len(self.roles)} role definitions "
                f"in {len(self.categories)} categories"
            )

        except FileNotFoundError:
            logger.error(f"Role definitions file not found: {self.definitions_path}")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing role definitions: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading roles: {e}")

    def get_role(self, role_id: str) -> Optional[RoleDefinition]:
        """
        Gets a specific role definition by its ID.

        Args:
            role_id: The ID of the role to retrieve.

        Returns:
            A RoleDefinition object if the role is found, otherwise None.
        """
        return self.roles.get(role_id)

    def get_all_roles(self) -> List[RoleDefinition]:
        """
        Gets a list of all loaded role definitions.

        Returns:
            A list of all RoleDefinition objects.
        """
        return list(self.roles.values())

    def get_roles_by_category(self, category: str) -> List[RoleDefinition]:
        """
        Gets all roles within a specific category.

        Args:
            category: The name of the category.

        Returns:
            A list of RoleDefinition objects in the specified category.
        """
        role_ids = self.categories.get(category, [])
        return [self.roles[rid] for rid in role_ids if rid in self.roles]

    def get_roles_with_capability(self, capability: str) -> List[RoleDefinition]:
        """
        Gets all roles that require a specific capability.

        Args:
            capability: The name of the capability.

        Returns:
            A list of RoleDefinition objects that require the specified capability.
        """
        return [
            role for role in self.roles.values()
            if role.has_capability(capability)
        ]

    def get_roles_with_all_capabilities(
        self,
        capabilities: List[str]
    ) -> List[RoleDefinition]:
        """
        Gets all roles that require all of a given list of capabilities.

        Args:
            capabilities: A list of capability names.

        Returns:
            A list of RoleDefinition objects that require all of the specified capabilities.
        """
        return [
            role for role in self.roles.values()
            if role.has_all_capabilities(capabilities)
        ]

    def get_roles_with_any_capability(
        self,
        capabilities: List[str]
    ) -> List[RoleDefinition]:
        """
        Gets all roles that require at least one of a given list of capabilities.

        Args:
            capabilities: A list of capability names.

        Returns:
            A list of RoleDefinition objects that require at least one of the specified capabilities.
        """
        return [
            role for role in self.roles.values()
            if role.has_any_capability(capabilities)
        ]

    def search_roles(self, query: str) -> List[RoleDefinition]:
        """
        Searches for roles by name, description, or ID.

        Args:
            query: The search query.

        Returns:
            A list of RoleDefinition objects that match the query.
        """
        query_lower = query.lower()
        results = []

        for role in self.roles.values():
            if (
                query_lower in role.name.lower()
                or query_lower in role.description.lower()
                or query_lower in role.role_id.lower()
            ):
                results.append(role)

        return results

    def validate_role_dependencies(self, role_id: str) -> bool:
        """
        Validates that all of a role's dependencies exist.

        Args:
            role_id: The ID of the role to validate.

        Returns:
            True if all dependencies exist, False otherwise.
        """
        role = self.get_role(role_id)
        if not role:
            return False

        for dep in role.dependencies:
            if dep not in self.roles:
                logger.warning(
                    f"Role {role_id} depends on non-existent role: {dep}"
                )
                return False

        return True

    def get_role_dependency_tree(self, role_id: str) -> List[str]:
        """
        Gets the full dependency tree for a given role.

        Args:
            role_id: The ID of the role.

        Returns:
            A list of all role IDs that the given role depends on, directly or indirectly.
        """
        role = self.get_role(role_id)
        if not role:
            return []

        dependencies = []
        to_process = role.dependencies.copy()

        while to_process:
            dep_id = to_process.pop(0)
            if dep_id not in dependencies:
                dependencies.append(dep_id)
                dep_role = self.get_role(dep_id)
                if dep_role:
                    to_process.extend(dep_role.dependencies)

        return dependencies

    def get_categories(self) -> List[str]:
        """
        Gets a list of all available role categories.

        Returns:
            A list of category names.
        """
        return list(self.categories.keys())

    def reload(self):
        """
        Reloads the role definitions from the YAML file.
        """
        self.roles.clear()
        self.categories.clear()
        self._load_definitions()

    def __len__(self) -> int:
        return len(self.roles)

    def __contains__(self, role_id: str) -> bool:
        return role_id in self.roles

    def __iter__(self):
        return iter(self.roles.values())


# Global role loader instance
_role_loader: Optional[RoleLoader] = None


def get_role_loader() -> RoleLoader:
    """
    Gets the global instance of the RoleLoader.

    Returns:
        The global RoleLoader instance.
    """
    global _role_loader
    if _role_loader is None:
        _role_loader = RoleLoader()
    return _role_loader


def get_role(role_id: str) -> Optional[RoleDefinition]:
    """
    A convenience function to get a role definition by its ID.

    Args:
        role_id: The ID of the role to retrieve.

    Returns:
        A RoleDefinition object if the role is found, otherwise None.
    """
    return get_role_loader().get_role(role_id)


def get_all_roles() -> List[RoleDefinition]:
    """
    A convenience function to get a list of all role definitions.

    Returns:
        A list of all RoleDefinition objects.
    """
    return get_role_loader().get_all_roles()
