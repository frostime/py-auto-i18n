import re
from collections.abc import Mapping

__all__ = ['deep_update', 'diff_objects','merge_objects']

def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, Mapping):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def diff_objects(obj1, obj2):
    diff = {}
    for key, value in obj1.items():
        if key not in obj2:
            diff[key] = value
        elif isinstance(value, dict) and isinstance(obj2[key], dict):
            nested_diff = diff_objects(value, obj2[key])
            if nested_diff:
                diff[key] = nested_diff
        elif value != obj2[key]:
            diff[key] = value
    return diff


def merge_objects(obj1, obj2):
    return deep_update(obj1.copy(), obj2)
