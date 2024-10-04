import json
from pathlib import Path
from typing import Union

import click
import yaml

from auto_i18n.config import get_global_config, get_project_config
from auto_i18n.gpt import send_gpt_request
from auto_i18n.utils import (
    ensure_no_md_code_block,
    extract_i18n_text,
    file_reader,
    file_writer,
    merge_objects,
    read_file,
    replace_i18n_in_code,
    write_file,
)


def ensure_valid_key(i18n_obj: Union[dict[str, str], str]):
    """检查所有的 key，只允许字母、数字，其他的所有符号全部去掉"""
    if isinstance(i18n_obj, str):
        return "".join(filter(str.isalnum, i18n_obj))

    checked_obj = {}
    for key, value in i18n_obj.items():
        new_key = "".join(filter(str.isalnum, key))
        checked_obj[new_key] = value
    return checked_obj


def extract_i18n(directory="."):
    config = get_project_config()
    global_config = get_global_config()

    code_files = config.get("code_files", ["*.ts", "*.svelte"])
    i18n_pattern = config.get("i18n_pattern", r"\(\((`$1`)\)\)")
    i18n_var_prefix = config.get("i18n_var_prefix", "i18n")

    files: list[Path] = []
    for pattern in code_files:
        files.extend(Path(directory).rglob(pattern))

    new_i18ns = {}

    for file in files:
        code = read_file(file)

        lines = extract_i18n_text(code, i18n_pattern)
        if not lines:
            continue

        prompt: str = global_config.get("prompt", {}).get("autokey", "")
        line_text = "\n".join(lines) if len(lines) > 1 else lines[0]
        prompt = prompt.replace(r"{lines}", line_text)

        result = send_gpt_request(prompt)
        result = ensure_no_md_code_block(result)
        try:
            new_i18n = json.loads(result)
        except json.JSONDecodeError:
            click.echo(f"Extract i18n failed for {file}, the GPT response is not a valid JSON.")
            click.echo(f"Error decoding GPT response: {result}")
            continue
        new_i18n = ensure_valid_key(new_i18n)

        # code_fpath = file.relative_to(directory).as_posix()
        # code_fname = file.name.replace(".", "")
        code_fname = ensure_valid_key(file.name)
        new_i18ns[code_fname] = new_i18n

        code = replace_i18n_in_code(
            code, new_i18n, i18n_pattern, f"{i18n_var_prefix}.{code_fname}"
        )

        write_file(file, code)

    update_main_i18n_file(new_i18ns)


def update_main_i18n_file(new_i18ns):
    config = get_project_config()
    i18n_dir = Path(config.get("i18n_dir", "src/i18n"))
    main_file = config.get("main_file", "zh_CN.yaml")

    main_file_path = i18n_dir / main_file
    with file_reader(main_file_path) as f:
        main_i18n = yaml.safe_load(f)

    if not main_i18n:
        main_i18n = {}

    for i18n_key, new_i18n in new_i18ns.items():
        file_i18n = main_i18n.get(i18n_key, {})
        file_i18n = merge_objects(file_i18n, new_i18n)
        main_i18n[i18n_key] = file_i18n

    with file_writer(main_file_path) as f:
        yaml.dump(main_i18n, f, allow_unicode=True)

    print(f"Updated main i18n file: {main_file_path}")
