# auto-i18n

[English README](README_en_US.md)


auto-i18n 是一个强大的命令行工具，旨在简化项目中的国际化（i18n）过程。它利用 GPT 自动化翻译并从代码中提取可翻译内容。

## 特性

- 自动从代码中提取可翻译字符串
- 使用 GPT 翻译 i18n 文件
- 灵活的配置选项，适用于全局和项目特定设置
- 支持多种文件格式（JSON、YAML）


## 快速开始

### 1. 初始化配置

首先安装 auto-i18n：

```bash
pip install auto-i18n
```

### 2. 配置 GPT 参数

auto-i18n 使用 GPT 来翻译，需要设置一下 GPT 的参数。运行以下命令：

```bash
i18n config set --global GPT.endpoint "https://api.openai.com/v1/chat/completions"
i18n config set --global GPT.key "你的_API_密钥"
i18n config set --global GPT.model "模型名称"
```

> 全局配置信息保存在 `~/.auto-i18n.yaml` 文件中。

运行 `testgpt` 命令测试一下 GPT 是否配置正确：

```bash
> i18n testgpt

Testing GPT, send: Hello, how are you?
GPT response: Hello! I'm here and ready to help. How can I assist you today?
```

### 3. 在你的项目中初始化

在你需要配置 i18n 的项目的根目录下，运行以下命令：

```bash
i18n init
```

这个命令会创建一个 `auto-i18n.project.yaml` 文件。别担心，我们稍后会详细解释这个文件的内容。

创建完成后，你首先应该根据自己项目的情况修改前面三个字段:

```yaml
code_files:  # 请在此处配置你的代码文件 glob 表达式
- '**/*.ts'
- '**/*.svelte'
i18n_dir: src/i18n  # 指定 i18n 文件的存放目录
main_file: zh_CN.yaml  # 指定主语言文件名
```

### 4. 在项目代码中直接书写文本

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
```

> [!NOTE]
> 这里使用 ((\`xxx\`)) 作为范例是因为示例为 javascript 语言。
> 你可以根据自己的项目语言来配置对应的模式，比如在 python 里面可以用 ((f'xxx'))。
>
> 外层使用了两个括号是因为几乎在所有语言里，`()` 都是合法的表达式语法，且几乎很少有实际的项目会连续使用两个 `()`。
> 这样就可以避免在对源代码进行不当侵入的情况下对 (需要自动翻译的) 特殊部分进行标记。

### 5. 自动提取 i18n 文本

在项目目录下运行:

```bash
i18n extract
```

程序会自动扫描所有匹配到的文本，并生成合适的名称，写入的 `main_file` 中。

```yaml
hello: 你好
samplesvelte:
  welcometoautoi18n: 欢迎来到 Auto-i18n
testts:
  initsuccesspleasecontinue: 初始化成功，请继续
```

同时，原本的 i18n 文本会自动被替换为对应的变量:

```ts
// src/test.ts
import { i18n } from 'somewhere-in-your-project';

const main = () => {
    console.log( i18n.testts.initsuccesspleasecontinue );
}
```

```svelte
<!-- src/component.svelte -->
<script>
    import { i18n } from 'somewhere-in-your-project';
</script>
<div>
    { i18n.samplesvelte.welcometoautoi18n }
</div>
```

### 6. 翻译 i18n 文本

运行以下命令翻译 i18n 文本：

```bash
i18n translate
```

程序会：

1. 读取 `main_file` 中的文本
2. 扫描 `i18n_dir` 下所有的其他语言的文件
3. 翻译内容，并合并到其他语言的文件中

```yaml
# en_US.yaml
hello: Hello
samplesvelte:
  welcometoautoi18n: Welcome to Auto-i18n
testts:
  initsuccesspleasecontinue: Initialization succeeded, please continue
```

## 配置选项

## 全局配置

存放在 `~/.auto-i18n.yaml` 文件中。

```yaml
GPT:
  endpoint: 
  key: 
  model: 
prompt:
  autokey: 
  translate: 

```

- `GPT.endpoint`: GPT API 的地址
- `GPT.key`: GPT API 的密钥
- `GPT.model`: GPT 模型名称
- `prompt.autokey`: 自动生成的翻译文本的前缀
- `prompt.translate`: 翻译文本的提示语

### 默认的 prompt.autokey

> ```md
> ## Task Description
>
> - Background: You are developing a project which need to using i18n variables for internationalization.
> - Task:
>   1. Read all the [## i18n text]
>   2. Generate appropriate key names based on the content of each text
>  3. Summarize the results into a JSON
> - **Output Format Requirements**:
>   - Retaining JSON format
>   - Output the JSON code directly, without attaching the ‍```json‍``` code block identifier
> - **Key Name Requirements**:
>   - **Only lowercase English letters and numbers are allowed**, no other special symbols (such as spaces, -, underscores, etc.)
>     - E.g. "greeting" and "invalidinputnumber" are valid, while "welcome_here", "invalid-input-number", and "非英文字符" are not valid
>     - **Keep short and concise**, each key name within 15 characters, upmost to 25 characters, it is ok to scacrifice readability for brevity.
>
> ## i18n Text
>
> ‍```txt
> {lines}
> ‍```
>
> ## An example, for reference only!
>
> Input:
>
> ‍```txt
> Hello {0}
> Warning! Please do not enter numbers outside 0-10!
> ‍```
>
> Output
>
> {
> "greeting": "Hello {0}",
> "invalidinputnumber": "Warning! Please do not enter numbers outside 0-10!"
> }
> ```

### 默认的 prompt.translate

> ```md
> ## Task Description
>
> - Task: Translate the content of the i18n file {InFile} (see [## i18n Content]) to another language (file {OutFile}).
> - Requirements:
>   - Target language file: {OutFile}
>   - Output format: JSON code, please retaining JSON format
>   - Output the translated JSON code directly, without attaching the ‍```json‍``` code block identifier
>
> ## Vocabulary
>
> {Dict}
>
> ## i18n Content
>
> ‍```json
> {I18n}
> ‍```
> ```

## 项目配置

通过 `init` 命令创建的 `auto-i18n.project.yaml` 文件内容如下：

```yaml
code_files:
- '**/*.ts'
- '**/*.svelte'
i18n_dir: temp/i18n
main_file: zh_CN.yaml
dict: {}
i18n_pattern: \(\(`(.+?)`\)\)
i18n_var_prefix: i18n
strategy: diff

```

- `i18n_dir`: 存放翻译文件的目录
- `main_file`: 主要语言的翻译文件
- `code_files`: 需要扫描的代码文件类型
- `i18n_pattern`: 在代码中标记需要翻译的文本的模式
- `dict`: 特殊词汇的翻译对照表
- `strategy`: 翻译策略，"diff" 表示只翻译新增的内容, "all" 表示翻译所有内容
- `i18n_var_prefix`: 在代码中使用的替换变量的前缀

你可以根据自己的需求修改这些配置。

### 覆盖全局配置

在项目配置中可以在 `global` 字段中指定全局配置的覆盖项，例如这样:

```yaml
code_files:
- '**/*.ts'
- '**/*.svelte'
i18n_dir: temp/i18n
main_file: zh_CN.yaml
dict: {}
i18n_pattern: \(\(`(.+?)`\)\)
i18n_var_prefix: i18n
strategy: diff
global:
  GPT:
    endpoint: "https://api.openai.com/v1/chat/completions"
    key: "你的_API_密钥"
    model: "模型名称"
```
