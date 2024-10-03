import click

from py_i18n.config import init_global_config, init_project_config
from py_i18n.extract import extract_i18n
from py_i18n.gpt import send_gpt_request
from py_i18n.translate import translate_i18n


@click.group()
def cli():
    init_global_config()


@cli.command()
def init():
    """Initialize the project configuration"""
    if init_project_config():
        click.echo("Project configuration file created successfully.")
    else:
        click.echo("Project configuration file already exists.")


@cli.command()
@click.option("--full/--diff", default=None, help="Translation strategy")
def translate(full):
    """Translate i18n files"""
    translate_i18n(full)


@cli.command()
@click.option("--dir", default=".", help="Directory to extract i18n from")
def extract(dir):
    """Extract i18n text from code files"""
    extract_i18n(dir)


@cli.command()
def testgpt():
    """Test the connection to GPT"""
    click.echo("Testing GPT, send: Hello, how are you?")
    res = send_gpt_request("Hello, how are you?")
    if res:
        click.echo(f"GPT response: {res}")
    else:
        click.echo("GPT request failed.", color="red")


if __name__ == "__main__":
    cli()
