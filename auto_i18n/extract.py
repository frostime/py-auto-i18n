import json
import re
from pathlib import Path
from typing import Union

import click

from auto_i18n.config import get_global_config_value, get_project_config_value
from auto_i18n.gpt import send_gpt_request
from auto_i18n.i18n import i18n
from auto_i18n.io import read_file, read_i18n_file, write_file, write_i18n_file
from auto_i18n.utils import echo, ensure_no_md_code_block, merge_objects, regex_findall

I18N = i18n()


def ensure_valid_key(i18n_obj: Union[dict[str, str], str]):
    """Check all keys, only allow letters and numbers, remove all other symbols"""
    if isinstance(i18n_obj, str):
        return ''.join(filter(str.isalnum, i18n_obj))

    checked_obj = {}
    for key, value in i18n_obj.items():
        new_key = ''.join(filter(str.isalnum, key))
        checked_obj[new_key] = value
    return checked_obj


def replace_i18n_in_code(code: str, i18n_dict: dict[str, str], pattern: str, prefix: str):
    def replacer(match):
        text = match.group(1)
        for key, value in i18n_dict.items():
            if value == text:
                return f'{prefix}.{key}'
        return match.group(0)

    return re.sub(pattern, replacer, code)


def extract_i18n(directory='.'):
    code_files = get_project_config_value('code_files', ['*.ts', '*.svelte'])
    i18n_pattern = get_project_config_value('i18n_pattern', r'\(\((`$1`)\)\)')
    i18n_var_prefix = get_project_config_value('i18n_var_prefix', 'i18n')

    project_code_files: list[Path] = []
    for pattern in code_files:
        project_code_files.extend(Path(directory).rglob(pattern))

    # click.echo(project_code_files)

    if not project_code_files:
        return

    new_i18ns = {}

    for code_file in project_code_files:
        click.echo(click.style(f'📝 {code_file}', fg='cyan'))
        code = read_file(code_file)

        lines = regex_findall(code, i18n_pattern)
        if not lines:
            click.echo(f'\t没有在 {code_file} 中找到 i18n 变量')
            continue

        prompt = get_global_config_value('prompt.autokey', '')
        line_text = '\n'.join(lines) if len(lines) > 1 else lines[0]
        prompt = prompt.replace(r'{lines}', line_text)

        result = send_gpt_request(prompt)
        result = ensure_no_md_code_block(result)
        try:
            new_i18n = json.loads(result)
        except json.JSONDecodeError:
            click.error(
                f'\t提取失败, GPT 没有返回一个正确的 JSON 文本, 以下是 GPT 的回答:\n {result}'
            )
            continue
        new_i18n = ensure_valid_key(new_i18n)

        code_fname = ensure_valid_key(code_file.name)
        new_i18ns[code_fname] = new_i18n

        for key, value in new_i18n.items():
            echo.debug(f'\t{i18n_var_prefix}.{code_fname}.{key}: "{value}"')
            if key in new_i18ns:
                echo.warning(f'\t🚨 ⚠️{key} 在 {code_fname} 下重复了!')

        code = replace_i18n_in_code(
            code, new_i18n, i18n_pattern, f'{i18n_var_prefix}.{code_fname}'
        )

        write_file(code_file, code)

    if new_i18ns:
        update_main_i18n_file(new_i18ns)
    else:
        echo.warning('无需更新 i18n 文件')


def update_main_i18n_file(new_i18ns):
    i18n_dir = Path(get_project_config_value('i18n_dir', 'src/i18n'))
    main_file = get_project_config_value('main_file', 'zh_CN.yaml')

    main_file_path = i18n_dir / main_file
    main_i18n = read_i18n_file(main_file_path)

    if not main_i18n:
        main_i18n = {}

    echo.info(f'⬆️ 更新 i18n 文件: {main_file_path}')

    for i18n_key, new_i18n in new_i18ns.items():
        file_i18n = main_i18n.get(i18n_key, {})
        file_i18n = merge_objects(file_i18n, new_i18n)
        main_i18n[i18n_key] = file_i18n

    write_i18n_file(main_file_path, main_i18n)
