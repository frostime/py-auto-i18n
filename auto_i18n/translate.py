import json
from pathlib import Path

import click
import yaml

from auto_i18n.config import get_global_config, get_project_config
from auto_i18n.gpt import send_gpt_request
from auto_i18n.utils import diff_objects, ensure_no_md_code_block, merge_objects


def translate_i18n(full=None):
    config = get_project_config()
    strategy = full if full is not None else config.get("strategy", "diff")
    i18n_dir = Path(config.get("i18n_dir", "src/i18n"))
    main_file = config.get("main_file", "zh_CN.yaml")

    main_file_path = i18n_dir / main_file
    with open(main_file_path, "r", encoding="utf-8") as f:
        in_obj = yaml.safe_load(f)

    if in_obj is None or len(in_obj) == 0:
        click.echo("No i18n data found in main file, translation aborted.", color="red")
        return

    out_files = list(i18n_dir.glob(f'*.{main_file.split(".")[-1]}'))
    out_files = [f for f in out_files if f != main_file_path]

    PROMPT = get_global_config().get("prompt", {}).get("translate", "")

    if PROMPT == "":
        click.echo("No prompt found in global config, translation aborted.", color="red")
        return

    for out_file in out_files:
        with open(out_file, "r", encoding="utf-8") as f:
            out_obj = yaml.safe_load(f)

        if out_obj is None:
            out_obj = {}

        if strategy == "diff":
            to_translate = diff_objects(in_obj, out_obj)
        else:
            to_translate = in_obj

        prompt = PROMPT.format(
            InFile=main_file,
            OutFile=out_file.name,
            Dict=json.dumps(config.get("dict", {})),
            I18n=json.dumps(to_translate),
        )

        result = send_gpt_request(prompt)
        result = ensure_no_md_code_block(result)
        try:
            translated = json.loads(result)
        except json.JSONDecodeError:
            click.echo(f"Translation failed for {out_file}, result is not a valid JSON.", color="red")
            continue

        merged = merge_objects(out_obj, translated)

        with open(out_file, "w", encoding="utf-8") as f:
            yaml.dump(merged, f, allow_unicode=True)

        print(f"Translated and updated {out_file}")
