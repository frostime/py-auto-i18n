from pathlib import Path
from typing import Any, Optional, TypedDict

from auto_i18n import io
from auto_i18n.utils import deep_update

CONFIG_FILE = Path.home() / ".auto-i18n.yaml"
PROJECT_CONFIG_FILE = "auto-i18n.project.yaml"

PROMPT_TRANSLATE = r"""
## Task Description

- Task: Translate the content of the i18n file {InFile} (see [## i18n Content]) to another language (file {OutFile}).
- Requirements:
  - Target language file: {OutFile}
  - Output format: JSON code, please retaining JSON format
  - Output the translated JSON code directly, without attaching the ```json``` code block identifier

## Vocabulary

{Dict}

## i18n Content

```json
{I18n}
```
""".strip()

PROMPT_AUTOKEY = r"""
## Task Description

- Background: You are developing a project which need to using i18n variables for internationalization.
- Task:
  1. Read all the [## i18n text]
  2. Generate appropriate key names based on the content of each text
 3. Summarize the results into a JSON
- **Output Format Requirements**:
  - Retaining JSON format
  - Output the JSON code directly, without attaching the ```json``` code block identifier
- **Key Name Requirements**:
  - **Only lowercase English letters and numbers are allowed**, no other special symbols (such as spaces, -, underscores, etc.)
    - E.g. "greeting" and "invalidinputnumber" are valid, while "welcome_here", "invalid-input-number", and "非英文字符" are not valid
  - **Keep short and concise**, each key name within 15 characters, upmost to 25 characters, it is ok to scacrifice readability for brevity.

## i18n Text

```txt
{lines}
```

## An example, for reference only!

Input:

```txt
Hello {0}
Warning! Please do not enter numbers outside 0-10!
```

Output

{
"greeting": "Hello {0}",
"invalidinputnumber": "Warning! Please do not enter numbers outside 0-10!"
}
""".strip()


class GPT(TypedDict):
    endpoint: str
    key: str
    model: str


class Prompt(TypedDict):
    translate: str
    autokey: str


class GlobalConfig(TypedDict):
    GPT: GPT
    prompt: Prompt


class ProjectConfig(TypedDict):
    i18n_dir: str
    main_file: str
    code_files: list[str]
    i18n_pattern: str
    dict: dict[str, str]
    strategy: str
    i18n_var_prefix: str
    global_config: Optional[GlobalConfig]


def get_global_config() -> GlobalConfig:
    global_config = io.read_yaml(CONFIG_FILE)
    project_config = get_project_config()

    if "global_config" in project_config and project_config["global_config"]:
        return deep_update(global_config, project_config["global_config"])

    return global_config


def get_project_config() -> ProjectConfig:
    return io.read_yaml(Path(PROJECT_CONFIG_FILE))


def init_global_config():
    if not CONFIG_FILE.exists():
        default_config: GlobalConfig = {
            "GPT": {
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "key": "",
                "model": "gpt-4o",
            },
            "prompt": {
                "translate": PROMPT_TRANSLATE,
                "autokey": PROMPT_AUTOKEY,
            },
        }
        io.write_yaml(default_config, CONFIG_FILE)


def init_project_config():
    if Path(PROJECT_CONFIG_FILE).exists():
        return False

    config: ProjectConfig = {
        "i18n_dir": "src/i18n",
        "main_file": "zh_CN.yaml",
        "code_files": ["*.ts", "*.svelte", "*.tsx", "*.vue"],
        "i18n_pattern": r"\(\(`(.+?)`\)\)",
        "dict": {},
        "strategy": "diff",
        "i18n_var_prefix": "i18n",
        "global_config": {},
    }

    # Auto-detect i18n directory
    for dir_name in ["i18n", "locale"]:
        if Path(dir_name).is_dir():
            config["i18n_dir"] = dir_name
            break

    io.write_yaml(config, PROJECT_CONFIG_FILE)
    return True


# New functions for config commands
def get_config_value(key: str, global_config=True, default=None):
    config = get_global_config() if global_config else get_project_config()
    keys = key.split(".")
    value = config
    for k in keys:
        if k in value:
            value = value[k]
        else:
            return default
    return value


def get_global_config_value(key: str, default=None):
    return get_config_value(key, global_config=True, default=default)


def get_project_config_value(key: str, default=None):
    return get_config_value(key, global_config=False, default=default)


def set_config_value(key: str, value: Any, global_config=True):
    config = get_global_config() if global_config else get_project_config()
    keys = key.split(".")
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    current[keys[-1]] = value
    io.write_yaml(config, CONFIG_FILE if global_config else PROJECT_CONFIG_FILE)


def list_config(global_config=True):
    return get_global_config() if global_config else get_project_config()
