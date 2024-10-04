import sys

import click
import requests

from auto_i18n.config import get_global_config
from auto_i18n.i18n import i18n

_ = i18n()

def send_gpt_request(prompt: str):
    config = get_global_config()
    endpoint = config["GPT"]["endpoint"]
    api_key = config["GPT"]["key"]
    model = config["GPT"]["model"]

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6,
    }

    TIMEOUT_SECONDS = None

    try:
        response = requests.post(
            endpoint, headers=headers, json=data, timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except Exception as e:
        click.echo(click.style(_.errors.connection_failed.format(error=str(e)), fg='red'))
        sys.exit(1)

    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        click.echo(click.style(_.errors.invalid_response, fg='red'))
        click.echo(f"Response Text: {response.text}")
        sys.exit(1)