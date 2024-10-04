import re

__all__ = [
    "ensure_no_md_code_block",
    "regex_findall",
    "replace_vars"
]

def ensure_no_md_code_block(s: str):
    """确保没有被 ``` 代码块包裹"""
    if s.endswith("```"):
        s = s[:-3]
    if s.lower().startswith("```json"):
        s = s[8:]
    if s.lower().startswith("```"):
        s = s[3:]
    return s


def regex_findall(code: str, pattern: str):
    return re.findall(pattern, code)


def replace_vars(text: str, vars: dict[str, str]):
    """替换文本中的变量

    所有变量使用 {变量名} 来定义，例如 {name}

    >>> replace_vars("Hello, {name}!", {"name": "world"})
    >>> "Hello, world!"
    """
    for key, value in vars.items():
        text = text.replace(f"{{{key}}}", value)
    return text

