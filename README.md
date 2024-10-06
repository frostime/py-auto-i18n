---
title: py-auto-i18n
date: 2024-10-04T21:41:08.000Z
lastmod: 2024-10-04T22:20:08.000Z
document: 20241004214108-5aymt55
notebook: Life
hpath: /我的项目/py-auto-i18n
export: '2024-10-04 22:20:16'
---

# auto-i18n

[English README](README_en_US.md)

auto-i18n 是一个基于 python 开发的命令行工具，旨在简化项目中的国际化（i18n）过程。它利用 GPT 自动化翻译并从代码中提取可翻译内容。

## 特性

* 自动从代码中提取可翻译字符串
* 自动生成 I18n 变量替换原始的文本
* 使用 GPT 翻译 i18n 文件
* 灵活的配置选项，适用于全局和项目特定设置

## 快速开始

### 1. 初始化配置

首先安装 auto-i18n：

```bash
pip install auto-i18n
```

安装后，你可以使用 `i18n`​ 或者 `auto-i18n`​ 来运行命令

### 2. 配置 GPT 参数

auto-i18n 使用 GPT 来翻译，需要设置一下 GPT 的参数。运行以下命令：

```bash
i18n config set --global GPT.endpoint "https://api.openai.com/v1/chat/completions"
i18n config set --global GPT.key "你的_API_密钥"
i18n config set --global GPT.model "模型名称"
```

> 全局配置信息保存在 `~/.auto-i18n.yaml`​ 文件中。

运行 `testgpt`​ 命令测试一下 GPT 是否配置正确：

```bash
> i18n testgpt

Testing GPT, send: Hello, how are you?
GPT response: Hello! I'm here and ready to help. How can I assist you today?
```

---

​`auto-i18n`​ 默认使用英文，如果你想要使用中文，可以运行

```bash
i18n config set --global lang "zh_CN"
```

### 3. 在你的项目中初始化

在你需要配置 i18n 的项目的根目录下，运行以下命令：

```bash
i18n init
```

这个命令会创建一个 `auto-i18n.project.yaml`​ 文件。

创建完成后，你首先应该根据自己项目的情况修改这几个字段:

```yaml
code_files:  # 请在此处配置你的代码文件 glob 表达式
- 'src/**/*.ts'
- 'src/**/*.svelte'
i18n_dir: src/i18n  # 指定 i18n 文件的存放目录
main_file: zh_CN.yaml  # 指定主语言文件名
i18n_pattern: \(\(`(.+?)`\)\)  # 指定需要翻译的文本的匹配模式，见下一节
```

### 4. 在项目代码中直接书写文本

​`auto-i18n`​ 基于模板匹配 + 字符串替换的方式来自动提取和翻译文本。在开发的时候，你需要直接在你的项目中使用符合 `i18n_pattern`​ 语法的字面量。

```
((`文本内容`))
```

例如这样（以下以一个前端项目为例）

```ts
// src/test.ts
import { i18n } from 'somewhere-in-your-project';

const main = () => {
    console.log( ((`初始化成功，请继续`)) );
}
```

```svelte
<!-- src/sample.svelte -->
<script>
    import { i18n } from 'somewhere-in-your-project';
</script>
<div>
    { ((`欢迎来到 Auto-i18n`)) }
</div>
```

> [!NOTE]  
> 这里使用 ((\`xxx\`)) 作为范例是因为示例为 javascript 语言。  
> 你可以根据自己的项目语言来配置对应的模式，比如在 python 里面可以配置为:
>
> ```yaml
> i18n_pattern: \(\(r"(.+?)"\)\)
> ```
>
> 然后在代码中写:
>
> ```py
> print( ((r"简单测试一下")) )
> ```
>
> 外层使用了两个括号是因为几乎在所有语言里，`()`​ 都是合法的表达式语法；这么写即便后面不使用 i18n 命令进行替换也能正常运行。考虑到几乎很少有实际的项目会连续使用两个 `()`​，这样就可以避免在对源代码进行不当侵入的情况下对 (需要自动翻译的) 特殊部分进行标记。

### 5. 自动提取 i18n 文本

在项目目录下运行:

```bash
i18n extract
```

程序会自动扫描所有匹配到的文本，并使用 GPT 来生成合适的 i18n 变量名称，写入的 `main_file`​ （如：zh_CN.yaml 文件）中。

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
<!-- src/sample.svelte -->
<script>
    import { i18n } from 'somewhere-in-your-project';
</script>
<div>
    { i18n.samplesvelte.welcometoautoi18n }
</div>
```

被替换的变量有三个部分组成:

1. ​`i18n_var_prefix`​: 可以在项目配置文件中设置
2. ​`filename`​: 一个基于当前文件名，只包含字母、数字的字面量
3. ​`i18n_var_name`​: 由 GPT 生成的变量名称

    > 如果变量名称出现了冲突，程序会自动的变量后面加上数字以避免命名冲突
    >

### 6. 翻译 i18n 文本

运行以下命令翻译 i18n 文本：

```bash
i18n translate
```

程序会：

1. 读取 `main_file`​ 中的文本，如 zh_CN.json 文件
2. 扫描 `i18n_dir`​ 下所有的其他语言的文件，如同目录的 en_US.json, ja_JP.json 文件
3. 使用 GPT 翻译内容，并合并到其他语言的文件中

```yaml
# en_US.yaml
hello: Hello
samplesvelte:
  welcometoautoi18n: Welcome to Auto-i18n
testts:
  initsuccesspleasecontinue: Initialization succeeded, please continue
```

> [!NOTE]
>
> 默认会使用 `--diff`​ 模式进行翻译，在该模式下程序只翻译增量部分，而不会全部翻译（以节省 token 和时间消耗）。
>
> 你可以通过指定 `--full`​ 参数要求程序完整翻译整个 i18n 文件。

### 7. 导出

使用 `export`​ 命令，可以将主 i18n 文件导出为其他格式，目前支持 TypeScript 接口 (.d.ts)。

```bash
i18n export
```

该命令会默认将导出的文件写入到项目目录下，你可以在 `auto-i18n.project.yaml`​中配置 `export_dir`​来指定其他目录。

## 配置选项

### 全局配置

存放在 `~/.auto-i18n.yaml`​ 文件中。

```yaml
GPT:
  endpoint: 
  key: 
  model: 
prompt:
  autokey: 
  translate: 
lang: 

```

* ​`GPT.endpoint`​: GPT API 的地址
* ​`GPT.key`​: GPT API 的密钥
* ​`GPT.model`​: GPT 模型名称
* ​`prompt.autokey`​: 用于自动生成的 i18n 变量前缀名称的 prompt
* ​`prompt.translate`​: 用于翻译文本的 prompt
* ​`lang`​: 使用的语言，可选为 `en_US`​ 和 `zh_CN`​

### 项目级配置

通过 `init`​ 命令创建的 `auto-i18n.project.yaml`​ 文件内容如下：

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
export_dir:
```

* ​`i18n_dir`​: 存放翻译文件的目录
* ​`main_file`​: 主要语言的翻译文件
* ​`code_files`​: 需要扫描的代码文件类型
* ​`i18n_pattern`​: 在代码中标记需要翻译的文本的模式
* ​`dict`​: 特殊词汇的翻译对照表；你可以把项目中涉及到的一些属于翻译写在这个地方
* ​`strategy`​: 翻译策略
  * `"diff"`​ 表示只翻译新增的内容
  * `"full"`​ 表示翻译所有内容
* ​`i18n_var_prefix`​: 在代码中使用的替换变量的前缀
* ​`export_dir`​: 导出目录，如果设置，将用作 export 命令的输出目录
* `i18n_var_mid`: i18n 键的中间部分生成策略。选项包括：
  * `"filename"`: 使用完整文件名，包含扩展名，如 `utilsts`
  * `"filename_noext"`: 使用不带扩展名的文件名
  * `"pathname"`: 使用文件的相对路径


### 覆盖全局配置

在项目配置中，可以在 `global_config`​ 字段中覆盖全局配置，例如这样:

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
global_config:
  GPT:
    endpoint: "https://api.openai.com/v1/chat/completions"
    key: "你的_API_密钥"
    model: "模型名称"
```

‍

## 其他说明

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
>   - Output the JSON code directly, without attaching the ‍‍‍```json‍‍‍``` code block identifier
> - **Key Name Requirements**:
>   - **Only lowercase English letters and numbers are allowed**, no other special symbols (such as spaces, -, underscores, etc.)
>     - E.g. "greeting" and "invalidinputnumber" are valid, while "welcome_here", "invalid-input-number", and "非英文字符" are not valid
>     - **Keep short and concise**, each key name within 15 characters, upmost to 25 characters, it is ok to scacrifice readability for brevity.
>
> ## i18n Text
>
> ‍‍‍```txt
> {lines}
> ‍‍‍```
>
> ## An example, for reference only!
>
> Input:
>
> ‍‍‍```txt
> Hello {0}
> Warning! Please do not enter numbers outside 0-10!
> ‍‍‍```
>
> Output
>
> {
> "greeting": "Hello {0}",
> "invalidinputnumber": "Warning! Please do not enter numbers outside 0-10!"
> }
> ```

本 prompt 在运行时将会替换如下变量：

* ​`{lines}`​：替换为在源代码文件中找到的所有 i18n 文本

  * 例如：如果源代码为:

    ```ts
    console.log(((`你好啊`)))
    ele.innerText = ((`警告!`))
    ```
  * 则 `{lines}`​ 会被替换为

    ```ts
    你好啊
    警告!
    ```

### 默认的 prompt.translate

> ```md
> ## Task Description
>
> - Task: Translate the content of the i18n file {InFile} (see [## i18n Content]) to another language (file {OutFile}).
> - Requirements:
>   - Target language file: {OutFile}
>   - Output format: JSON code, please retaining JSON format
>   - Output the translated JSON code directly, without attaching the ‍‍‍```json‍‍‍``` code block identifier
>
> ## Vocabulary
>
> {Dict}
>
> ## i18n Content
>
> ‍‍‍```json
> {I18n}
> ‍‍‍```
> ```

本 prompt 在运行时将会替换如下变量：

* ​`{InFile}`​：你的主 i18n 文件的文件名，例如 `zh_CN.json`​
* ​`{OutFile}`​：将要翻译的目标 i18n 文件，例如 `ja_JP.json`​
* ​`{Dict}`​: Project 配置中的 `dict`​ 字段
* ​`{I18n}`​: 需要被翻译的 i18n 对应的 json 字符串
