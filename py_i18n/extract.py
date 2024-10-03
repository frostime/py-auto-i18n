import json
from pathlib import Path

import yaml

from py_i18n.config import get_global_config, get_project_config
from py_i18n.gpt import send_gpt_request
from py_i18n.utils import extract_i18n_text, merge_objects, replace_i18n_in_code


def ensure_valid_key(i18n_obj: dict[str, str]):
    """检查所有的 key，只允许字母、数字，其他的所有符号全部去掉"""
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
        with open(file, "r", encoding="utf-8") as f:
            code = f.read()

        lines = extract_i18n_text(code, i18n_pattern)
        if not lines:
            continue

        prompt: str = global_config.get("prompt", {}).get("autokey", "")
        line_text = "\n".join(lines) if len(lines) > 1 else lines[0]
        prompt = prompt.replace(r'{lines}', line_text)

        result = send_gpt_request(prompt)
        new_i18n = json.loads(result)
        new_i18n = ensure_valid_key(new_i18n)

        # code_fpath = file.relative_to(directory).as_posix()
        code_fname = file.name.replace('.', '')
        new_i18ns[code_fname] = new_i18n

        code = replace_i18n_in_code(code, new_i18n, i18n_pattern, f'{i18n_var_prefix}.{code_fname}')

        with open(file, "w", encoding="utf-8") as f:
            f.write(code)

    update_main_i18n_file(new_i18ns)


def update_main_i18n_file(new_i18ns):
    config = get_project_config()
    i18n_dir = Path(config.get("i18n_dir", "src/i18n"))
    main_file = config.get("main_file", "zh_CN.yaml")

    main_file_path = i18n_dir / main_file
    with open(main_file_path, "r", encoding="utf-8") as f:
        main_i18n = yaml.safe_load(f)

    for i18n_key, new_i18n in new_i18ns.items():
        file_i18n = main_i18n.setdefault(i18n_key, {})
        file_i18n = merge_objects(file_i18n, new_i18n)
        main_i18n[i18n_key] = file_i18n

    with open(main_file_path, "w", encoding="utf-8") as f:
        yaml.dump(main_i18n, f, allow_unicode=True)

    print(f"Updated main i18n file: {main_file_path}")