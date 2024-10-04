import json
import os
from pathlib import Path
from typing import Union

import yaml

FilePath = Union[Path, str]


def file_reader(file_path: FilePath):
    return open(file_path, 'r', encoding='utf-8')


def file_writer(file_path: FilePath):
    return open(file_path, 'w', encoding='utf-8')


def read_file(file_path: FilePath):
    with file_reader(file_path) as f:
        return f.read()


def write_file(file_path: FilePath, content: str):
    with file_writer(file_path) as f:
        f.write(content)


def read_yaml(file_path: FilePath):
    if Path(file_path).exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError:
            return {}
    return {}


def write_yaml(file_path: FilePath, data: dict):
    def str_presenter(dumper, data):
        if len(data.splitlines()) > 1:  # check for multiline string
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    yaml.add_representer(str, str_presenter)

    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def read_json(file_path: FilePath):
    if Path(file_path).exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def write_json(file_path: FilePath, data: dict):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# 根据文件后缀名，自动选择对应的读写函数
def read_i18n_file(file_path: FilePath):
    file_path = Path(file_path)
    if file_path.suffix.lower() == '.yaml' or file_path.suffix.lower() == '.yml':
        return read_yaml(file_path)
    elif file_path.suffix.lower() == '.json':
        return read_json(file_path)
    else:
        raise ValueError(f'Unsupported file format: {file_path.suffix}')


# 根据文件后缀名，自动选择对应的读写函数
def write_i18n_file(file_path: FilePath, data: dict):
    file_path = Path(file_path)
    if file_path.suffix.lower() == '.yaml' or file_path.suffix.lower() == '.yml':
        write_yaml(file_path, data)
    elif file_path.suffix.lower() == '.json':
        write_json(file_path, data)
    else:
        raise ValueError(f'Unsupported file format: {file_path.suffix}')
