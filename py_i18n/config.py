import os
from pathlib import Path

import yaml

CONFIG_FILE = Path.home() / ".py-i18n.yaml"
PROJECT_CONFIG_FILE = "py-i18n.project.yaml"

PROMPT_TRANSLATE = """
## 任务描述

- 任务: 请将 i18n 文件 {InFile} 的内容（见[## i18n 内容]）翻译到 {OutFile} 文件的语言中
- 要求: 
  - 目标语言文件: {OutFile}
  - 翻译为 json 语言，注意要保留原始的 json 格式
  - 将翻译的 json 代码直接输出，不需要附带 ‍```json ‍``` 的代码块标识

## 词汇表

{Dict}

## i18 内容

‍```json
{I18n}
‍```
""".strip()

PROMPT_AUTOKEY = """
## 任务描述

- 背景: 你正在开发一个项目，现在需要把文本替换为 i18n 变量
- 任务: 你的任务是阅读所有的[## i18n 文本]，然后根据各个文本内容生成合适的 key 名称，最后将结果汇总到一个 json 中
- 输出格式要求: 
  - 使用 json 语言，保留 json 格式
  - 将 json 代码直接输出，不需要附带 ‍```json ‍``` 的代码块标识
- key 名称要求: 全小写英文字母，可以有数字，但是不含任何特殊符号 (包括 -, _ 等)

## i18n 文本

‍```txt
{lines}
‍```

## 案例

输入 i18n 文本如下:

‍```txt
你好 {0}
警告！请不要输入 0-10 之外的数字！
‍```

你仔细阅读了文本内容，分析内在的语义；最后输出:

{
  "greeting": "你好 {0}",
  "invalidinputnumber": "警告！请不要输入 0-10 之外的数字！"
}
""".strip()


def load_config(file_path):
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def save_config(config, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True)


def get_global_config():
    return load_config(CONFIG_FILE)


def get_project_config():
    return load_config(Path(PROJECT_CONFIG_FILE))


def init_global_config():
    if not CONFIG_FILE.exists():
        default_config = {
            "GPT": {
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "key": "",
                "model": "gpt-4o",
            },
            "prompt": {
                "translate": PROMPT_TRANSLATE,  # Default translate prompt
                "autokey": PROMPT_AUTOKEY,  # Default autokey prompt
            },
        }
        save_config(default_config, CONFIG_FILE)


def init_project_config():
    if Path(PROJECT_CONFIG_FILE).exists():
        return False

    config = {
        "i18n_dir": "src/i18n",
        "main_file": "zh_CN.yaml",
        "code_files": ["*.ts", "*.svelte", "*.tsx", "*.vue"],
        "i18n_pattern": r"\(\((`$1`)\)\)",
        "dict": {},
        "strategy": "diff",
        "i18n_var_prefix": "i18n",
    }

    # Auto-detect i18n directory
    for dir_name in ["i18n", "locale"]:
        if Path(dir_name).is_dir():
            config["i18n_dir"] = dir_name
            break

    save_config(config, PROJECT_CONFIG_FILE)
    return True
