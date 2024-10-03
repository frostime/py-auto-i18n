import requests

from py_i18n.config import get_global_config


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

    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error sending GPT request: {e}")
        return None

    return response.json()["choices"][0]["message"]["content"]
