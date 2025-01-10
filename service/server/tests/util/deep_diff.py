import json
from typing import Any, Callable


def deep_diff(left: Any, right: Any) -> Any:
    if isinstance(left, dict) and isinstance(right, dict):
        return dict_diff(left, right)
    if isinstance(left, list) and isinstance(right, list):
        return list_diff(left, right)
    if isinstance(left, Callable):  # type: ignore
        return None if left(right) else left
    if isinstance(right, Callable):  # type: ignore
        return None if right(left) else right
    if left != right:
        return f"{left} != {right}"
    return None


def dict_diff(left: dict, right: dict) -> dict | None:
    diff = {}
    all_keys = set(left.keys()) | set(right.keys())
    for key in all_keys:
        if key not in left:
            key_diff = "missing from left"
        elif key not in right:
            key_diff = "missing from right"
        else:
            key_diff = deep_diff(left[key], right[key])
        if key_diff:
            diff[key] = key_diff
    return diff or None


def list_diff(left: list, right: list) -> dict | None:
    diff = {}
    len1, len2 = len(left), len(right)
    for i in range(max(len1, len2)):
        if i >= len1:
            index_diff = "missing from left"
        elif i >= len2:
            index_diff = "missing from right"
        else:
            index_diff = deep_diff(left[i], right[i])
        if index_diff:
            diff[f"Index {i}"] = index_diff
    return diff or None


def pretty_diff(left: Any, right: Any) -> str | None:
    diff = deep_diff(left, right)
    if not diff:
        return None
    return json.dumps(diff, indent=2)
