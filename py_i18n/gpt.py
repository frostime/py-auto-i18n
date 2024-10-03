import requests

from py_i18n.config import get_global_config


def send_gpt_request(prompt):
    config = get_global_config()
    endpoint = config['GPT']['endpoint']
    api_key = config['GPT']['key']
    model = config['GPT']['model']

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.7
    }

    response = requests.post(endpoint, headers=headers, json=data)
    response.raise_for_status()

    return response.json()['choices'][0]['message']['content']