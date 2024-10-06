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
from auto_i18n.utils.string import replace_vars

I18N = i18n()


def ensure_valid_key(
    i18n_obj: Union[dict[str, str], str], convert_to_underscore: bool = False
):
    """
    Check all keys, only allow letters, numbers, and underscores.
    Optionally convert other symbols to underscores.
    """

    def clean_key(key: str) -> str:
        if convert_to_underscore:
            return ''.join(c if c.isalnum() or c == '_' else '_' for c in key)
        else:
            return ''.join(filter(lambda c: c.isalnum() or c == '_', key))

    if isinstance(i18n_obj, str):
        return clean_key(i18n_obj)

    checked_obj = {}
    for key, value in i18n_obj.items():
        new_key = clean_key(key)
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
    i18n_var_mid = get_project_config_value('i18n_var_mid', 'filename')

    project_code_files: list[Path] = []
    for pattern in code_files:
        project_code_files.extend(Path(directory).rglob(pattern))

    if not project_code_files:
        return

    new_i18ns = {}

    for code_file in project_code_files:
        click.echo(click.style(f'📝 {code_file}', fg='cyan'))
        code = read_file(code_file)

        lines = regex_findall(code, i18n_pattern)
        if not lines:
            click.echo(
                replace_vars(
                    I18N.extractpy.notfoundi18nvar, {'code_file': str(code_file)}
                )
            )
            continue

        prompt = get_global_config_value('prompt.autokey', '')
        line_text = '\n'.join(lines) if len(lines) > 1 else lines[0]
        prompt = prompt.replace(r'{lines}', line_text)

        result = send_gpt_request(prompt)
        result = ensure_no_md_code_block(result)
        try:
            new_i18n = json.loads(result)
        except json.JSONDecodeError:
            echo.error(replace_vars(I18N.extractpy.extractionfail, {'result': result}))
            continue
        new_i18n = ensure_valid_key(new_i18n, convert_to_underscore=True)

        if i18n_var_mid == 'filename':
            middle_key = ensure_valid_key(code_file.name, convert_to_underscore=True)
        elif i18n_var_mid == 'filename_noext':
            middle_key = ensure_valid_key(code_file.stem, convert_to_underscore=True)
        elif i18n_var_mid == 'pathname':
            middle_key = ensure_valid_key(
                str(code_file.relative_to(directory)).replace('/', '_').replace('\\', '_')
            )
        else:
            middle_key = ensure_valid_key(code_file.name)  # Fallback to full filename

        new_i18ns[middle_key] = new_i18n

        for key, value in new_i18n.items():
            echo.debug(f'\t{i18n_var_prefix}.{middle_key}.{key}: "{value}"')
            if key in new_i18ns:
                # echo.warning(f'\t🚨 ⚠️{key} 在 {code_fname} 下重复了!')
                echo.warning(
                    replace_vars(
                        I18N.extractpy.duplicatekey,
                        {'key': key, 'code_fname': middle_key},
                    )
                )
                suffix = 1
                while f'{key}{suffix}' in new_i18ns:
                    suffix += 1

                echo.warning(
                    replace_vars(
                        I18N.extractpy.avoidconflict, {'0': key, '1': f'{key}{suffix}'}
                    )
                )
                key = f'{key}{suffix}'

        code = replace_i18n_in_code(
            code, new_i18n, i18n_pattern, f'{i18n_var_prefix}.{middle_key}'
        )

        write_file(code_file, code)

    if new_i18ns:
        update_main_i18n_file(new_i18ns)
    else:
        echo.warning(I18N.extractpy.noupdatei18nfile)


def update_main_i18n_file(new_i18ns):
    i18n_dir = Path(get_project_config_value('i18n_dir', 'src/i18n'))
    main_file = get_project_config_value('main_file', 'zh_CN.yaml')

    main_file_path = i18n_dir / main_file
    main_i18n = read_i18n_file(main_file_path)

    if not main_i18n:
        main_i18n = {}

    # echo.info(f'⬆️ 更新 i18n 文件: {main_file_path}')
    echo.info(
        replace_vars(I18N.extractpy.updatei18nfile, {'main_file_path': main_file_path})
    )

    for i18n_key, new_i18n in new_i18ns.items():
        file_i18n = main_i18n.get(i18n_key, {})
        file_i18n = merge_objects(file_i18n, new_i18n)
        main_i18n[i18n_key] = file_i18n

    write_i18n_file(main_file_path, main_i18n)
