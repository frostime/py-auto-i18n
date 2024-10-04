import json
import os

from auto_i18n.gpt import send_gpt_request

PROMPT = r"""
- 为了测试某个 i18n 工具，需要一些示例文件
- 请你阅读 {工具说明}，理解工具的用法和需要满足 extract 命令的格式
- 分别生成:
  - 一个使用了 ((``)) 语法的 typescript 样例代码文件, 内容随机，不和样例重复
  - 一个使用了 ((``)) 语法的 svelte 样例代码文件, 内容随机，不和样例重复
  - 注，为了保证生成内容的随机性
    1. 首先给自己想象一个实际的应用场景
    2. 然后在这个场景中，生成可能会用到的文本
    3. 每个文件里面至少有 3 处地方使用了 ((``)) 语法; 并且至少有一处的文本长度足够长（至少大于 50 字），以测试工具的处理能力
- 输出格式: 将生成结果汇总到一个纯 json 代码中发给我，注意不包含 ```json 等 md code block标签
{
    "ts-code.ts": "纯 ts 样例代码",
    "svelte-code.svelte": "纯 svelte 样例代码"
}

## 工具说明

在开发的时候，你可以在你的项目中使用如下语法直接书写字面值:

```
((`文本内容`))
```

例如这样:

```ts
// src/test.ts
import { i18n } from 'somewhere-in-your-project';

const main = () => {
    console.log( ((`初始化成功，请继续`)) );
}
```

```svelte
<!-- src/component.svelte -->
<script>
    import { i18n } from 'somewhere-in-your-project';
</script>
<div>
    { ((`欢迎来到 Auto-i18n`)) }
</div>

"""

def ch_dir():
    i = 0
    # 一直向上切换，直到 pyproject.toml 所在目录
    while i < 3 and not os.path.exists("pyproject.toml"):
        os.chdir("..")
        i += 1
    print(os.getcwd())

def ensure_dir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

def main():
    ch_dir()

    response = send_gpt_request(PROMPT)
    print(response)
    obj = json.loads(response)

    ensure_dir('temp/codes/')
    ensure_dir('temp/i18n/')

    for filename, content in obj.items():
        with open(f'temp/codes/{filename}', 'w', encoding='utf-8') as f:
            f.write(content)

    I18N_FILES = ['zh_CN', 'en_US', 'ja_JP']
    FORMAT = 'yaml'
    for filename in I18N_FILES:
        with open(f'temp/i18n/{filename}.{FORMAT}', 'w', encoding='utf-8') as f:
            f.write('')


if __name__ == '__main__':
    main()
