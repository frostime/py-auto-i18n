import os
from pathlib import Path

import yaml

CUR_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


class DottedDict(dict):
    def __getattr__(self, key: str):
        value = self[key]
        if isinstance(value, dict):
            return DottedDict(value)
        return value

    def __getitem__(self, key: str):
        value = super().__getitem__(key)
        if isinstance(value, dict):
            return DottedDict(value)
        return value


def i18n(lang: str = 'en_US') -> DottedDict:
    i18n_file = CUR_DIR / f'{lang}.yaml'
    with open(i18n_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return DottedDict(data)