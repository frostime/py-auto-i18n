import sys

import click
import requests

from auto_i18n.config import get_global_config


def send_gpt_request(prompt):
    config = get_global_config()
    endpoint = config["GPT"]["endpoint"]
    api_key = config["GPT"]["key"]
    model = config["GPT"]["model"]

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    TIMEOUT_SECONDS = 10

    try:
        response = requests.post(
            endpoint, headers=headers, json=data, timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except Exception as e:
        click.echo(f"Connection failed. Error sending request to GPT: {e}", err=True, color=True)
        sys.exit(1)

    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        click.echo(
            "ERROR: API returned an invalid GPT response, Please check your API key and endpoint.",
            err=True,
            color=True,
        )
        click.echo(f"Response Text\n: {response.text}", err=True, color=False)
        sys.exit(1)
