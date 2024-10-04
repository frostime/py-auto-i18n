import click


def echo(msg: str, fg: str = None, bold: bool = False):
    click.echo(click.style(msg, fg=fg, bold=bold))


def debug(msg: str):
    click.echo(click.style(msg))


def info(msg: str):
    click.echo(click.style(msg, fg='cyan'))


def warning(msg: str):
    click.echo(click.style(msg, fg='yellow'))


def error(msg: str):
    click.echo(click.style(msg, fg='red'))
