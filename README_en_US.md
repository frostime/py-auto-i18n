# auto-i18n

[中文文档](README.md)

auto-i18n is a powerful command-line tool designed to simplify the internationalization (i18n) process in projects. It leverages GPT to automate translations and extract translatable content from code.

## Features

- Automatically extract translatable strings from code
- Use GPT to translate i18n files
- Flexible configuration options, suitable for both global and project-specific settings
- Supports multiple file formats (JSON, YAML)


## Quick Start

### 1. Initialize Configuration

First, install auto-i18n:

```bash
pip install auto-i18n
```

### 2. Configure GPT Parameters

auto-i18n uses GPT for translation. You need to configure the GPT parameters by running the following commands:

```bash
i18n config set --global GPT.endpoint "https://api.openai.com/v1/chat/completions"
i18n config set --global GPT.key "your_API_key"
i18n config set --global GPT.model "model_name"
```

> Global configuration is stored in the `~/.auto-i18n.yaml` file.

Run `testgpt` to test the GPT API connection:

```bash
> i18n testgpt

Testing GPT, send: Hello, how are you?
GPT response: Hello! I'm here and ready to help. How can I assist you today?
```

### 3. Initialize in Your Project

In the root directory of the project where you want to set up i18n, run the following command:

```bash
i18n init
```

This command will create an `auto-i18n.project.yaml` file. Don’t worry, we’ll explain the contents of this file later.

After creation, you should first modify the following three fields according to your project:

```yaml
code_files:  # Configure the glob expression for your code files here
- '**/*.ts'
- '**/*.svelte'
i18n_dir: src/i18n  # Specify the directory for i18n files
main_file: zh_CN.yaml  # Specify the main language file name
```

### 4. Write Text Directly in Your Project Code

When developing, you can directly write literals in your project using the following syntax:

```
((`text content`))
```

For example:

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
> Here, ((\`xxx\`)) is used as an example because the example is in the JavaScript language.
> You can configure the corresponding pattern according to your project language, for example, in Python, you can use ((f'xxx')).
>
> The outer layer uses two parentheses because in almost all languages, `()` is a legal expression syntax, and it is rare for actual projects to use two consecutive `()`.
> This way, it can avoid marking special parts (to be translated) in a way that intrudes on the source code.

### 5. Automatically Extract i18n Text

Run the following command in your project directory:

```bash
i18n extract
```

The program will automatically scan all matched text and generate appropriate key names, writing them into the `main_file`.

```yaml
hello: 你好
samplesvelte:
  welcometoautoi18n: 欢迎来到 Auto-i18n
testts:
  initsuccesspleasecontinue: 初始化成功，请继续
```

At the same time, the original i18n text in the code will be automatically replaced by the corresponding variable:

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

### 6. Translate i18n Text

Run the following command to translate i18n text:

```bash
i18n translate
```

The program will:

1. Read the text from the `main_file`.
2. Scan all other language files in the `i18n_dir`.
3. Translate the content and merge it into the other language files.

```yaml
# en_US.yaml
hello: Hello
samplesvelte:
  welcometoautoi18n: Welcome to Auto-i18n
testts:
  initsuccesspleasecontinue: Initialization succeeded, please continue
```

## Configuration Options

### Global Configuration

Stored in the `~/.auto-i18n.yaml` file.

```yaml
GPT:
  endpoint: 
  key: 
  model: 
prompt:
  autokey: 
  translate: 
```

- `GPT.endpoint`: The GPT API address
- `GPT.key`: The GPT API key
- `GPT.model`: The GPT model name
- `prompt.autokey`: The prefix for auto-generated translation keys
- `prompt.translate`: The prompt for translating texts

### Default `prompt.autokey`

> ```md
> ## Task Description
>
> - Background: You are developing a project that requires using i18n variables for internationalization.
> - Task:
>   1. Read all the [## i18n text].
>   2. Generate appropriate key names based on the content of each text.
>   3. Summarize the results into JSON.
> - **Output Format Requirements**:
>   - Retain JSON format.
>   - Output the JSON code directly, without attaching the ```json``` code block identifier.
> - **Key Name Requirements**:
>   - **Only lowercase English letters and numbers are allowed**, no other special symbols (such as spaces, -, underscores, etc.).
>     - For example, "greeting" and "invalidinputnumber" are valid, while "welcome_here", "invalid-input-number", and "non-English characters" are not valid.
>   - **Keep short and concise**, each key name within 15 characters, upmost to 25 characters, it is ok to scacrifice readability for brevity.
>
> ## i18n Text
>
> ```txt
> {lines}
> ```
>
> ## Example, for reference only!
>
> Input:
>
> ```txt
> Hello {0}
> Warning! Please do not enter numbers outside 0-10!
> ```
>
> Output
>
> {
> "greeting": "Hello {0}",
> "invalidinputnumber": "Warning! Please do not enter numbers outside 0-10!"
> }
> ```

### Default `prompt.translate`

> ```md
> ## Task Description
>
> - Task: Translate the content of the i18n file {InFile} (see [## i18n Content]) to another language (file {OutFile}).
> - Requirements:
>   - Target language file: {OutFile}.
>   - Output format: JSON code, please retain JSON format.
>   - Output the translated JSON code directly, without attaching the ```json``` code block identifier.
>
> ## Vocabulary
>
> {Dict}
>
> ## i18n Content
>
> ```json
> {I18n}
> ```
> ```

## Project Configuration

The content of the `auto-i18n.project.yaml` file created by the `init` command is as follows:

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

- `i18n_dir`: Directory where translation files are stored
- `main_file`: Main language translation file
- `code_files`: Types of code files to scan
- `i18n_pattern`: Pattern for identifying text that needs translation in code
- `dict`: Translation dictionary for specific terms
- `strategy`: Translation strategy: "diff" means only translate newly added content, "all" means translate all content
- `i18n_var_prefix`: Prefix for replacement variables used in code

You can modify these configurations based on your project’s needs.

### Override Global Configuration

You can override global configuration for a specific project by adding a `global_config` section to the project configuration file. For example:

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
    key: "Keys"
```
