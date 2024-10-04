import json
from pathlib import Path

import click

from auto_i18n import io
from auto_i18n.config import get_global_config_value, get_project_config
from auto_i18n.gpt import send_gpt_request
from auto_i18n.i18n import i18n
from auto_i18n.utils import (
    diff_objects,
    ensure_no_md_code_block,
    merge_objects,
    replace_vars,
)

I18N = i18n()


def translate_i18n(full=None):
    config = get_project_config()
    strategy = full if full is not None else config.get('strategy', 'diff')
    i18n_dir = Path(config.get('i18n_dir', 'src/i18n'))
    main_file = config.get('main_file', 'zh_CN.yaml')

    main_file_path = i18n_dir / main_file
    in_obj = io.read_i18n_file(main_file_path)

    if in_obj is None or len(in_obj) == 0:
        click.echo(click.style(I18N.translate.no_data, fg='red'))
        return

    out_files = list(i18n_dir.glob(f'*.{main_file.split(".")[-1]}'))
    out_files = [f for f in out_files if f != main_file_path]

    PROMPT = get_global_config_value('prompt.translate', default='')

    if PROMPT == '':
        click.echo(click.style(I18N.translate.no_prompt, fg='red'))
        return

    for out_file in out_files:
        out_obj = io.read_i18n_file(out_file)

        if out_obj is None:
            out_obj = {}

        if strategy == 'diff':
            to_translate = diff_objects(in_obj, out_obj)
        else:
            to_translate = in_obj

        prompt = replace_vars(
            PROMPT,
            {
                'InFile': main_file,
                'OutFile': out_file.name,
                'Dict': json.dumps(config.get('dict', {})),
                'I18n': json.dumps(to_translate),
            },
        )

        result = send_gpt_request(prompt)
        result = ensure_no_md_code_block(result)
        try:
            translated = json.loads(result)
        except json.JSONDecodeError:
            click.echo(click.style(I18N.translate.failed.format(file=out_file), fg='red'))
            continue

        merged = merge_objects(out_obj, translated)

        io.write_i18n_file(out_file, merged)

        click.echo(click.style(I18N.translate.success.format(file=out_file), fg='green'))
