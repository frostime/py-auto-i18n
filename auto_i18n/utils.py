import re
from collections.abc import Mapping


def file_reader(file_path):
    return open(file_path, "r", encoding="utf-8")


def file_writer(file_path):
    return open(file_path, "w", encoding="utf-8")


def read_file(file_path):
    with file_reader(file_path) as f:
        return f.read()


def write_file(file_path, content):
    with file_writer(file_path) as f:
        f.write(content)


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


def extract_i18n_text(code, pattern):
    return re.findall(pattern, code)


def replace_i18n_in_code(code, i18n_dict, pattern, prefix):
    def replacer(match):
        text = match.group(1)
        for key, value in i18n_dict.items():
            if value == text:
                return f"{prefix}.{key}"
        return match.group(0)

    return re.sub(pattern, replacer, code)
