"""
Safe expression evaluator for workflow conditions.
"""

from __future__ import annotations

import ast
import operator
from typing import Any

from faccp_common.exceptions import ValidationError

_BINARY_OPS = {
    ast.Eq: operator.eq, ast.NotEq: operator.ne,
    ast.Lt: operator.lt, ast.LtE: operator.le,
    ast.Gt: operator.gt, ast.GtE: operator.ge,
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.Not: operator.not_, ast.USub: operator.neg, ast.UAdd: operator.pos}
_BOOL_OPS = {ast.And: all, ast.Or: any}


def evaluate_condition(condition: str, variables: dict[str, Any], event_payload: dict[str, Any] | None = None) -> bool:
    try:
        tree = ast.parse(condition, mode="eval")
        result = _eval_node(tree.body, variables, event_payload or {})
        return bool(result)
    except SyntaxError as e:
        raise ValidationError(f"Invalid condition syntax: {e}")
    except Exception as e:
        raise ValidationError(f"Condition evaluation failed: {e}")


def _eval_node(node: ast.AST, variables: dict[str, Any], event_payload: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in variables:
            return variables[node.id]
        if node.id in event_payload:
            return event_payload[node.id]
        if node.id == "true": return True
        if node.id == "false": return False
        if node.id in ("null", "none"): return None
        raise ValidationError(f"Unknown variable: {node.id}")
    if isinstance(node, ast.Attribute):
        if isinstance(node.value, ast.Name) and node.value.id == "event":
            return event_payload.get(node.attr)
        if isinstance(node.value, ast.Name) and node.value.id in variables:
            v = variables[node.value.id]
            if isinstance(v, dict):
                return v.get(node.attr)
        raise ValidationError(f"Attribute access not supported: {node.attr}")
    if isinstance(node, ast.Subscript):
        container = _eval_node(node.value, variables, event_payload)
        if isinstance(container, (list, dict, str)):
            if isinstance(node.slice, ast.Constant):
                return container[node.slice.value]
        raise ValidationError("Invalid subscript")
    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, variables, event_payload)
        for op, comparator in zip(node.ops, node.comparators):
            right = _eval_node(comparator, variables, event_payload)
            op_type = type(op)
            if op_type not in _BINARY_OPS:
                raise ValidationError(f"Operator {op_type.__name__} not allowed")
            if not _BINARY_OPS[op_type](left, right):
                return False
            left = right
        return True
    if isinstance(node, ast.BoolOp):
        op_type = type(node.op)
        if op_type not in _BOOL_OPS:
            raise ValidationError(f"Bool operator {op_type.__name__} not allowed")
        values = [_eval_node(v, variables, event_payload) for v in node.values]
        return _BOOL_OPS[op_type](bool(v) for v in values)
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _UNARY_OPS:
            raise ValidationError(f"Unary operator {op_type.__name__} not allowed")
        return _UNARY_OPS[op_type](_eval_node(node.operand, variables, event_payload))
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _BINARY_OPS:
            raise ValidationError(f"Operator {op_type.__name__} not allowed")
        return _BINARY_OPS[op_type](
            _eval_node(node.left, variables, event_payload),
            _eval_node(node.right, variables, event_payload),
        )
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            fname = node.func.id
            if fname == "len" and len(node.args) == 1:
                return len(_eval_node(node.args[0], variables, event_payload))
            if fname == "int" and len(node.args) == 1:
                return int(_eval_node(node.args[0], variables, event_payload))
            if fname == "str" and len(node.args) == 1:
                return str(_eval_node(node.args[0], variables, event_payload))
            if fname == "contains" and len(node.args) == 2:
                a = _eval_node(node.args[0], variables, event_payload)
                b = _eval_node(node.args[1], variables, event_payload)
                return b in a
        raise ValidationError("Function not allowed")
    if isinstance(node, ast.List):
        return [_eval_node(elt, variables, event_payload) for elt in node.elts]
    if isinstance(node, ast.Dict):
        return {
            _eval_node(k, variables, event_payload): _eval_node(v, variables, event_payload)
            for k, v in zip(node.keys, node.values)
        }
    if isinstance(node, ast.IfExp):
        test = _eval_node(node.test, variables, event_payload)
        return _eval_node(node.body if test else node.orelse, variables, event_payload)
    raise ValidationError(f"Expression type {type(node).__name__} not allowed")


class ExpressionEvaluator:

    def __init__(self, variables: dict[str, Any], event_payload: dict[str, Any] | None = None) -> None:
        self.variables = variables
        self.event_payload = event_payload or {}

    def eval(self, condition: str) -> bool:
        return evaluate_condition(condition, self.variables, self.event_payload)
