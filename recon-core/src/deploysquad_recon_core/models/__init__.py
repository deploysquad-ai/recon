"""Node type models for the project graph."""
from __future__ import annotations

from .project import ProjectNode
from .goal import GoalNode
from .version import VersionNode
from .persona import PersonaNode
from .constraint import ConstraintNode
from .module import ModuleNode
from .decision import DecisionNode
from .user_story import UserStoryNode
from .epic import EpicNode
from .feature import FeatureNode
from .base import BaseNode, Wikilink, FullStatus, NoCompleteStatus

NODE_TYPE_MAP: dict[str, type[BaseNode]] = {
    "project": ProjectNode,
    "goal": GoalNode,
    "version": VersionNode,
    "persona": PersonaNode,
    "constraint": ConstraintNode,
    "module": ModuleNode,
    "decision": DecisionNode,
    "user-story": UserStoryNode,
    "epic": EpicNode,
    "feature": FeatureNode,
}


def get_model_for_type(node_type: str) -> type[BaseNode]:
    """Get the Pydantic model class for a node type string.

    Raises KeyError if the type is not registered.
    """
    return NODE_TYPE_MAP[node_type]
