"""
Parser for workflow DSL.
"""

from __future__ import annotations

import json
from typing import Any

import yaml
from faccp_common.exceptions import ValidationError

from faccp_common.dsl.workflow import State, Transition, Workflow


class WorkflowParseError(Exception):
    pass


class WorkflowParser:

    @staticmethod
    def parse(source: str, format: str = "yaml") -> Workflow:
        try:
            if format == "yaml":
                data = yaml.safe_load(source)
            elif format == "json":
                data = json.loads(source)
            else:
                raise WorkflowParseError(f"Unknown format: {format}")
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise WorkflowParseError(f"Parse error: {e}")
        return WorkflowParser.from_dict(data)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Workflow:
        try:
            states = [State(**s) for s in data.get("states", [])]
            transitions = [Transition(**t) for t in data.get("transitions", [])]
            wf = Workflow(
                name=data["name"],
                version=data.get("version", "1.0"),
                description=data.get("description", ""),
                states=states,
                transitions=transitions,
                actions=data.get("actions", {}),
                variables=data.get("variables", {}),
            )
            wf.validate()
            return wf
        except KeyError as e:
            raise WorkflowParseError(f"Missing required field: {e}")
        except TypeError as e:
            raise WorkflowParseError(f"Invalid field type: {e}")
        except ValidationError as e:
            raise WorkflowParseError(f"Validation error: {e}")

    @staticmethod
    def to_yaml(workflow: Workflow) -> str:
        data = {
            "name": workflow.name,
            "version": workflow.version,
            "description": workflow.description,
            "states": [s.__dict__ for s in workflow.states],
            "transitions": [t.__dict__ for t in workflow.transitions],
            "actions": workflow.actions,
            "variables": workflow.variables,
        }
        return yaml.dump(data, default_flow_style=False, sort_keys=False)

    @staticmethod
    def to_dict(workflow: Workflow) -> dict[str, Any]:
        return {
            "name": workflow.name,
            "version": workflow.version,
            "description": workflow.description,
            "states": [s.__dict__ for s in workflow.states],
            "transitions": [t.__dict__ for t in workflow.transitions],
            "actions": workflow.actions,
            "variables": workflow.variables,
        }
