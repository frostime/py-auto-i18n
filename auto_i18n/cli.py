import click
import yaml

from auto_i18n.config import (
    get_config_value,
    init_global_config,
    init_project_config,
    list_config,
    set_config_value,
)
from auto_i18n.extract import extract_i18n
from auto_i18n.gpt import send_gpt_request
from auto_i18n.i18n import i18n
from auto_i18n.translate import translate_i18n

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
def init():
    """Initialize the project configuration."""
    click.echo(click.style(I18N.init.description, fg='blue', bold=True))
    click.echo(I18N.init.help)
    if init_project_config():
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
    if is_global == is_project:
        click.echo(click.style(I18N.config.list.error, fg='red'))
        return
    config = list_config(is_global)
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


if __name__ == '__main__':
    cli()
