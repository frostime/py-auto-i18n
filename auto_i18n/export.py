import json
from pathlib import Path

import click

from auto_i18n.config import get_project_config
from auto_i18n.i18n import i18n
from auto_i18n.io import read_i18n_file

I18N = i18n()


def export_i18n(format: str, export_dir: Path):
    if format != 'd.ts':
        click.echo(
            click.style(I18N.export.unsupported_format.format(format=format), fg='red')
        )
        return

    config = get_project_config()
    i18n_dir = Path(config.get('i18n_dir', 'src/i18n'))
    main_file = config.get('main_file', 'zh_CN.yaml')

    main_file_path = i18n_dir / main_file
    i18n_data = read_i18n_file(main_file_path)

    if i18n_data is None or len(i18n_data) == 0:
        click.echo(click.style(I18N.export.no_data, fg='red'))
        return

    ts_interface = convert_to_interface(i18n_data)

    output_file = export_dir / 'i18n.d.ts'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(ts_interface)

    click.echo(click.style(I18N.export.success.format(file=output_file), fg='green'))


def convert_to_interface(obj, interface_name='I18n'):
    return generate_interface(obj, interface_name)


def spaces(level=0):
    return ' ' * (level * 4)


def process_value(value, depth):
    if isinstance(value, str):
        return 'string'
    if isinstance(value, (int, float)):
        return 'number'
    if isinstance(value, bool):
        return 'boolean'
    if value is None:
        return 'null'
    if isinstance(value, list):
        if len(value) == 0:
            return 'any[]'
        item_types = [process_value(item, depth) for item in value]
        unique_types = list(set(item_types))
        if len(unique_types) == 1:
            return f'{unique_types[0]}[]'
        else:
            return f'[{", ".join(item_types)}]'
    if isinstance(value, dict):
        return generate_interface(value, depth=depth + 1)
    return 'any'


def generate_interface(obj, interface_name=None, depth=0):
    if not isinstance(obj, dict):
        return process_value(obj, depth)

    lines = [
        f'{spaces(depth)}interface {interface_name} {"{"}' if interface_name else '{'
    ]

    def add_property(key, value):
        type_ = process_value(value, depth)
        if not key.isalnum():
            key = f'"{key}"'
            click.echo(click.style(I18N.export.invalid_key.format(key=key), fg='yellow'))
        lines.append(f'{spaces(depth+1)}{key}: {type_};')

    for key, value in obj.items():
        add_property(key, value)

    lines.append(f'{spaces(depth)}}}')
    return '\n'.join(lines)
