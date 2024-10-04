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
from auto_i18n.translate import translate_i18n


@click.group()
def cli():
    """
    auto-i18n: A CLI tool for managing i18n in your projects.

    This tool helps you extract translatable strings from your code,
    manage translations, and integrate with GPT for automated translation.
    """
    init_global_config()


@cli.command()
def init():
    """
    Initialize the project configuration.

    This command creates a new project configuration file (auto-i18n.project.yaml)
    in the current directory. If the file already exists, it will not be overwritten.
    """
    if init_project_config():
        click.echo("Project configuration file created successfully.")
    else:
        click.echo("Project configuration file already exists.")


@cli.command()
@click.option(
    "--full/--diff", default=None, help="Use full translation or diff strategy."
)
def translate(full):
    """
    Translate i18n files.

    This command translates the main i18n file to other language files.
    It can either translate the full file or only the differences (based on the strategy).

    Options:
    --full: Translate the entire file.
    --diff: Only translate the differences (default if not specified).
    """
    translate_i18n(full)


@cli.command()
@click.option("--dir", default=".", help="Directory to extract i18n from.")
def extract(dir):
    """
    Extract i18n text from code files.

    This command scans the specified directory (default: current directory)
    for code files and extracts translatable strings based on the configured pattern.

    Options:
    --dir: The directory to scan for code files (default: current directory).
    """
    extract_i18n(dir)


@cli.command()
def testgpt():
    """
    Test the connection to GPT.

    This command sends a test message to the configured GPT endpoint
    to verify that the connection and authentication are working correctly.
    """
    click.echo("Testing GPT, send: Hello, how are you?")
    res = send_gpt_request("Hello, how are you?")
    if res:
        click.echo(f"GPT response: {res}")
    else:
        click.echo("GPT request failed.", color="red")


@cli.group()
def config():
    """
    Manage configuration settings.

    This group of commands allows you to view and modify both global and project-specific configurations.
    """
    pass


@config.command("list")
@click.option(
    "--global",
    "is_global",
    is_flag=True,
    default=False,
    help="List global configuration.",
)
@click.option(
    "--project",
    "is_project",
    is_flag=True,
    default=False,
    help="List project configuration.",
)
def config_list(is_global, is_project):
    """
    List configuration settings.

    This command displays either the global or project-specific configuration.
    You must specify either --global or --project.

    Options:
    --global: List the global configuration.
    --project: List the project-specific configuration.
    """
    if is_global == is_project:
        click.echo("Please specify either --global or --project")
        return
    config = list_config(is_global)
    click.echo(yaml.dump(config, allow_unicode=True))


@config.command("get")
@click.option(
    "--global", "is_global", is_flag=True, default=False, help="Get global configuration."
)
@click.option(
    "--project",
    "is_project",
    is_flag=True,
    default=False,
    help="Get project configuration.",
)
@click.argument("key")
def config_get(is_global, is_project, key):
    """
    Get a specific configuration value.

    This command retrieves the value of a specific configuration key.
    You must specify either --global or --project.

    Arguments:
    key: The configuration key to retrieve (can be nested, e.g., 'GPT.endpoint').

    Options:
    --global: Get the value from the global configuration.
    --project: Get the value from the project-specific configuration.
    """
    if is_global == is_project:
        click.echo("Please specify either --global or --project")
        return
    value = get_config_value(key, is_global)
    if value is None:
        click.echo(f"Key '{key}' not found in configuration")
    else:
        click.echo(yaml.dump({key: value}, allow_unicode=True))


@config.command("set")
@click.option(
    "--global", "is_global", is_flag=True, default=False, help="Set global configuration."
)
@click.option(
    "--project",
    "is_project",
    is_flag=True,
    default=False,
    help="Set project configuration.",
)
@click.argument("key")
@click.argument("value")
def config_set(is_global, is_project, key, value):
    """
    Set a configuration value.

    This command sets the value of a specific configuration key.
    You must specify either --global or --project.

    Arguments:
    key: The configuration key to set (can be nested, e.g., 'GPT.endpoint').
    value: The value to set. This will be parsed as YAML, so you can set complex values.

    Options:
    --global: Set the value in the global configuration.
    --project: Set the value in the project-specific configuration.
    """
    if is_global == is_project:
        click.echo("Please specify either --global or --project")
        return
    try:
        # Try to parse the value as YAML
        parsed_value = yaml.safe_load(value)
    except yaml.YAMLError:
        # If parsing fails, use the raw string
        parsed_value = value
    set_config_value(key, parsed_value, is_global)
    click.echo(f"Configuration updated: {key} = {parsed_value}")


if __name__ == "__main__":
    cli()
