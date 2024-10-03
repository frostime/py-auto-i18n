import json
from pathlib import Path

import yaml

from py_i18n.config import get_project_config
from py_i18n.gpt import send_gpt_request
from py_i18n.utils import diff_objects, merge_objects


def translate_i18n(full=None):
    config = get_project_config()
    strategy = full if full is not None else config.get("strategy", "diff")
    i18n_dir = Path(config.get("i18n_dir", "src/i18n"))
    main_file = config.get("main_file", "zh_CN.yaml")

    main_file_path = i18n_dir / main_file
    with open(main_file_path, "r", encoding="utf-8") as f:
        in_obj = yaml.safe_load(f)

    out_files = list(i18n_dir.glob(f'*.{main_file.split(".")[-1]}'))
    out_files = [f for f in out_files if f != main_file_path]

    for out_file in out_files:
        with open(out_file, "r", encoding="utf-8") as f:
            out_obj = yaml.safe_load(f)

        if strategy == "diff":
            to_translate = diff_objects(in_obj, out_obj)
        else:
            to_translate = in_obj

        prompt = config.get("prompt", {}).get("translate", "")
        prompt = prompt.format(
            InFile=main_file,
            OutFile=out_file.name,
            Dict=json.dumps(config.get("dict", {})),
            I18n=json.dumps(to_translate),
        )

        result = send_gpt_request(prompt)
        translated = json.loads(result)

        merged = merge_objects(out_obj, translated)

        with open(out_file, "w", encoding="utf-8") as f:
            yaml.dump(merged, f, allow_unicode=True)

        print(f"Translated and updated {out_file}")
