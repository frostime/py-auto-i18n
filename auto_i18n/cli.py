from pathlib import Path

import click
import yaml

from auto_i18n.config import (
    get_config_value,
    get_project_config_value,
    init_global_config,
    init_project_config,
    list_config,
    set_config_value,
)
from auto_i18n.export import export_i18n
from auto_i18n.extract import extract_i18n
from auto_i18n.gpt import send_gpt_request
from auto_i18n.i18n import i18n
from auto_i18n.translate import translate_file, translate_i18n
from auto_i18n.utils import echo

# Initialize i18n
I18N = i18n()


@click.group(help=I18N.cli.help)
def cli():
    """
    auto-i18n: A CLI tool for managing i18n in your projects.
    """
    click.echo(click.style(I18N.cli.description, fg='green', bold=True))
    click.echo(I18N.cli.help)
    init_global_config()


@cli.command(help=I18N.init.help)
@click.option(
    '--overwrite', is_flag=True, default=False, help=I18N.cli_py.force_cover_config
)
def init(overwrite):
    """Initialize the project configuration."""
    click.echo(click.style(I18N.init.description, fg='blue', bold=True))
    click.echo(I18N.init.help)
    if init_project_config(overwrite):
        click.echo(click.style(I18N.init.success, fg='green'))
    else:
        click.echo(click.style(I18N.init.already_exists, fg='yellow'))


@cli.command(help=I18N.translate.help)
@click.option('--full/--diff', default=None)
def translate(full):
    """Translate i18n files."""
    click.echo(click.style(I18N.translate.description, fg='blue', bold=True))
    click.echo(I18N.translate.help)
    click.echo(I18N.translate.options.full if full else I18N.translate.options.diff)
    click.echo(click.style(I18N.translate.start, fg='yellow'))
    translate_i18n(full)


@cli.command(name='translate-file', help=I18N.cli_py.specifyinputfile)
@click.option(
    '--in',
    'in_file',
    required=True,
    type=click.Path(exists=True),
    help=I18N.cli_py.specifyinputfilepath,
)
@click.option(
    '--out',
    'out_file',
    required=True,
    type=click.Path(),
    help=I18N.cli_py.specifyoutputfilepath,
)
@click.option('--lang', default='English', help=I18N.cli_py.specifytargetlang)
def translate_file_cmd(in_file: str, out_file: str, lang: str = 'English'):
    """Translate i18n files."""
    echo.info(f'"{in_file}" --> "{out_file}"[{lang}]')
    translate_file(in_file, out_file, lang)


@cli.command(help=I18N.extract.help)
@click.option('--dir', default='.', help=I18N.extract.options.dir)
def extract(dir):
    """Extract i18n text from code files."""
    click.echo(click.style(I18N.extract.description, fg='blue', bold=True))
    click.echo(I18N.extract.help)
    click.echo(I18N.extract.options.dir.format(directory=dir))
    click.echo(click.style(I18N.extract.start, fg='yellow'))
    extract_i18n(dir)


@cli.command(help=I18N.testgpt.help)
def testgpt():
    """Test the connection to GPT."""
    click.echo(click.style(I18N.testgpt.description, fg='blue', bold=True))
    click.echo(I18N.testgpt.help)
    click.echo(click.style(I18N.testgpt.start, fg='yellow'))
    res = send_gpt_request('Hello, how are you?')
    if res:
        click.echo(click.style(I18N.testgpt.success.format(response=res), fg='green'))
    else:
        click.echo(click.style(I18N.testgpt.failed, fg='red'))


@cli.group(help=I18N.config.help)
def config():
    """Manage configuration settings."""
    click.echo(click.style(I18N.config.description, fg='blue', bold=True))
    click.echo(I18N.config.help)


@config.command('list', help=I18N.config.list.help)
@click.option(
    '--global',
    'is_global',
    is_flag=True,
    default=False,
    help=I18N.config.list.options['global'],
)
@click.option(
    '--project',
    'is_project',
    is_flag=True,
    default=False,
    help=I18N.config.list.options['project'],
)
def config_list(is_global, is_project):
    """List configuration settings."""
    click.echo(click.style(I18N.config.list.description, fg='blue', bold=True))
    click.echo(I18N.config.list.help)
    if is_global and is_project:
        click.echo(click.style(I18N.config.list.error, fg='red'))
        return
    if is_project:
        config = list_config(False)
    else:
        config = list_config(True)
    click.echo(yaml.dump(config, allow_unicode=True))


@config.command('get', help=I18N.config.getter.help)
@click.option(
    '--global',
    'is_global',
    is_flag=True,
    default=False,
    help=I18N.config.getter.options['global'],
)
@click.option(
    '--project',
    'is_project',
    is_flag=True,
    default=False,
    help=I18N.config.getter.options['project'],
)
@click.argument('key')
def config_get(is_global, is_project, key):
    """Get a specific configuration value."""
    click.echo(click.style(I18N.config.getter.description, fg='blue', bold=True))
    click.echo(I18N.config.getter.help)
    if is_global == is_project:
        click.echo(click.style(I18N.config.getter.error.specify, fg='red'))
        return
    value = get_config_value(key, is_global)
    if value is None:
        click.echo(
            click.style(I18N.config.getter.error.not_found.format(key=key), fg='red')
        )
    else:
        click.echo(yaml.dump({key: value}, allow_unicode=True))


@config.command('set', help=I18N.config.setter.help)
@click.option(
    '--global',
    'is_global',
    is_flag=True,
    default=False,
    help=I18N.config.setter.options['global'],
)
@click.option(
    '--project',
    'is_project',
    is_flag=True,
    default=False,
    help=I18N.config.setter.options['project'],
)
@click.argument('key')
@click.argument('value')
def config_set(is_global, is_project, key, value):
    """Set a configuration value."""
    click.echo(click.style(I18N.config.setter.description, fg='blue', bold=True))
    click.echo(I18N.config.setter.help)
    if is_global == is_project:
        click.echo(click.style(I18N.config.setter.error.specify, fg='red'))
        return
    try:
        parsed_value = yaml.safe_load(value)
    except yaml.YAMLError:
        parsed_value = value
    set_config_value(key, parsed_value, is_global)
    click.echo(
        click.style(
            I18N.config.setter.success.format(key=key, value=parsed_value), fg='green'
        )
    )


@config.command(
    'edit',
    help=I18N.config.edit.help
    if hasattr(I18N.config, 'edit')
    else 'Edit the configuration file directly',
)
@click.option(
    '--global',
    'is_global',
    is_flag=True,
    default=False,
    help=I18N.config.edit.options['global']
    if hasattr(I18N.config, 'edit')
    else 'Edit the global configuration file',
)
@click.option(
    '--project',
    'is_project',
    is_flag=True,
    default=False,
    help=I18N.config.edit.options['project']
    if hasattr(I18N.config, 'edit')
    else 'Edit the project configuration file',
)
def config_edit(is_global, is_project):
    """Edit the configuration file directly."""
    if hasattr(I18N.config, 'edit'):
        click.echo(click.style(I18N.config.edit.description, fg='blue', bold=True))
        click.echo(I18N.config.edit.help)
    else:
        click.echo(click.style('Edit Configuration', fg='blue', bold=True))
        click.echo('Edit the configuration file directly with your system editor.')

    if is_global == is_project:
        error_msg = (
            I18N.config.edit.error.specify
            if hasattr(I18N.config, 'edit') and hasattr(I18N.config.edit, 'error')
            else 'Please specify either --global or --project'
        )
        click.echo(click.style(error_msg, fg='red'))
        return

    import os
    import platform
    import subprocess

    # Determine which config file to edit
    if is_global:
        from auto_i18n.config import CONFIG_FILE

        config_file = CONFIG_FILE
    else:
        from auto_i18n.config import PROJECT_CONFIG_FILE

        config_file = os.path.join(os.getcwd(), PROJECT_CONFIG_FILE)

    # Ensure the file exists
    if not os.path.exists(config_file):
        error_msg = (
            I18N.config.edit.error.not_found.format(file=config_file)
            if hasattr(I18N.config, 'edit') and hasattr(I18N.config.edit, 'error')
            else f'Config file not found: {config_file}'
        )
        click.echo(click.style(error_msg, fg='red'))
        return

    # Open the file with the system's default editor
    try:
        if platform.system() == 'Windows':
            os.startfile(config_file)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', config_file], check=True)
        else:  # Linux and other Unix-like systems
            # Try to use the default editor from environment variables
            editor = os.environ.get('EDITOR', 'vi')
            subprocess.run([editor, config_file], check=True)

        success_msg = (
            I18N.config.edit.success
            if hasattr(I18N.config, 'edit')
            else f'Opened config file for editing: {config_file}'
        )
        click.echo(click.style(success_msg, fg='green'))
    except Exception as e:
        error_msg = (
            I18N.config.edit.error.failed.format(error=str(e))
            if hasattr(I18N.config, 'edit') and hasattr(I18N.config.edit, 'error')
            else f'Failed to open config file: {str(e)}'
        )
        click.echo(click.style(error_msg, fg='red'))


@cli.command(help=I18N.export.help)
@click.option('--format', default='d.ts', help=I18N.export.options.format)
def export(format):
    """Export i18n files to other formats."""
    click.echo(click.style(I18N.export.description, fg='blue', bold=True))
    click.echo(I18N.export.help)
    click.echo(I18N.export.options.format.format(format=format))
    click.echo(click.style(I18N.export.start, fg='yellow'))

    export_dir = get_project_config_value('export_dir')
    if export_dir:
        export_dir = Path(export_dir)
    else:
        export_dir = Path.cwd()

    export_i18n(format, export_dir)


if __name__ == '__main__':
    cli()
