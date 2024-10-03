## 自动 i18n 工具

* Context：我正在开发自己的项目项目，但是困扰于 i18n 方案
* Task: 请你帮我开发一个基于 python 的 cli 程序，用来帮我处理一些杂项的问题；项目名称为 `py-i18n`
* 大致功能

  * 使用 GPT 翻译 i18n 文件
  * 从代码中根据模板自动提取需要翻译的片段，并完成翻译、替换等工作
* 安装之后 CLI 程序的名称: `i18n` 或者 `i18n-py`，两个等效，可以使用软链接来创建 alias

### CLI 程序功能需求描述

* CLI 程序配置

  * Global 配置：保存文件配置，存储在 ~/.py-i18n.yaml 文件中

    * GPT.endpoint：GPT api 的 url，可以配置，默认为 GPT 官方 api 地址
    * GPT.key：api key
    * prompt.translate: 翻译的 Prompt，多行文本；默认为:

      ```md
      ## 任务描述

      - 任务: 请将 i18n 文件 {InFile} 的内容（见[## i18n 内容]）翻译到 {OutFile} 文件的语言中
      - 要求: 
        - 目标语言文件: {OutFile}
        - 翻译为 json 语言，注意要保留原始的 json 格式
        - 将翻译的 json 代码直接输出，不需要附带 ‍‍```json ‍‍``` 的代码块标识

      ## 词汇表

      {Dict}

      ## i18 内容

      ‍‍```json
      {I18n}
      ‍‍```
      ```
    * prompt.autokey: 自动生成 i18n 文本的 key 名称；默认为

      ```md
      ## 任务描述

      - 背景: 你正在开发一个项目，现在需要把文本替换为 i18n 变量
      - 任务: 你的任务是阅读所有的[## i18n 文本]，然后根据各个文本内容生成合适的 key 名称，最后将结果汇总到一个 json 中
      - 输出格式要求: 
        - 使用 json 语言，保留 json 格式
        - 将 json 代码直接输出，不需要附带 ‍‍```json ‍‍``` 的代码块标识
      - key 名称要求: 全小写英文字母，可以有数字，但是不含任何特殊符号 (包括 -, _ 等)

      ## i18n 文本

      ‍‍```txt
      {lines}
      ‍‍```

      ## 案例

      输入 i18n 文本如下:

      ‍‍```txt
      你好 {0}
      警告！请不要输入 0-10 之外的数字！
      ‍‍```

      你仔细阅读了文本内容，分析内在的语义；最后输出:

      {
        "greeting": "你好 {0}",
        "invalidinputnumber": "警告！请不要输入 0-10 之外的数字！"
      }
      ```
  * Project 配置：对于一个需要处理 i18n 的项目，存储一些特定的配置信息；配置文件名称为 `py-i18n.project.yaml`

    * i18n_dir: string, 存放 i18n 文件（json 或者 yaml）的目录（相对项目的根目录的相对路径）
    * main_file：string，主 i18n 文件，例如 `zh_CN.yaml`，代表了 `i18n_dir/main_file` 这个文件被视为主 i18n 文件
    * code_files: string[], 项目下所有的代码文件，支持 glob 语法；例如 `["*.ts, *.svelte"]` 代表了一个基于 ts 和 svelte 开发的项目
    * i18n_pattern: string，可以被视为需要“自动抽取”的 i18n 文本的模板，默认为 `\(\(`($1)`\)\)`
    * dict: 词典，指定了本项目在翻译的时候可以用到的词汇表
    * strategy: `full | diff`，翻译时候的两种策略；默认为 `diff`
    * i18n_var_prefix: string, 默认为 `i18n`
* 初始化

  * CLI 程序在第一次运行的时候，检查全局的配置文件，如果不存在，就创建全局配置文件
  * `init` 命令：在运行 `i18n init` 之后，会在当前目录下创建一个 Project 配置文件

    * 首先会扫描所有的目录，如果有一个目录名叫 `i18n` 或者 `locale` ，就会自动把 `i18n_dir` 配置为这个目录
  * 此后，程序在运行的时候，每次都会自动读取全局配置和当前目录的配置文件，以此获取配置信息
* `translate [--full | --diff]` 命令：翻译当前 project 的 i18n；`--full` 和 `--diff` 为可选参数，可以临时覆盖 project 级别的 `strategy` 配置

  1. 获取 `i18n_dir/main_file` 的内容，转换为一个 dict 对象 `in_obj`；确定 mainFile 的格式
  2. 获取 `i18n_dir/` 下所有同格式的文件，保存为 `out_files`
  3. for each `out_file` in `out_files`

      * 读取 `out_file` 的内容，转换为一个 dict 对象 `out_obj`
      * 如果为 `diff` 

        * 计算 `in_obj` 和 `out_obj` 两个对象的差异——这一步的目的是，避开那些已经被翻译过的，只保留还需要翻译的
        * 将计算后的差异赋值给 `in_obj`
      * 如果为 `full` ，那就直接使用原始的 `in_obj`
      * 填充 prompt.translate，替换模板变量

        * 读取全局配置的 prompt
        * 将 `in_obj` 格式化为 json 格式
        * 将 `in_obj` 替换 prompt 中的 {I18n}
        * 将 {InFile} {OutFile} {Dict} 这些模板中的变量替换为实际的取值
      * 发送 GPT 请求
      * 获取翻译结果，解析 json 字符串

        * 首先检查一下是不是纯 json 字符串，如果被 ``` 代码块语法报告，需要做特别处理
        * 然后将 json 字符串 load 到 `result` 变量当中
      * 合并 `out_obj` 和 `result`
      * 将合并结果 format 为对应的 json 或者 yaml 格式中，然后写入 `out_file`
* `extract [--dir]` 命令：从代码当中自动提取 i18n 文本；默认从当前目录开始，`--dir` 参数可以指定对某个目录下的代码进行 i18n 提取

  1. 从 `dir` 目录下，递归地迭代所有的文件，根据 `code_files` 中的模板匹配所有代码文件，保存为变量 `files`
  2. 维护一个变量 `new_i18ns = {}`
  3. for file in files

      1. 读取 file 的内容 `code`
      2. 分析 `code` 中所有符合 `i18n_pattern` 的内容，将他们汇总到一个文本列表当中 `lines`
      3. 填充 prompt.autokey，替换模板变量

          1. 将 `{lines}` 替换为实际的 `lines.join('\n\')`
      4. 发送 GPT 请求
      5. 获取GPT返回结果，解析 json 字符串，并解析为一个 dict 变量 `new_i18n`
      6. `new_i18ns[filename] = new_i18n`
      7. 替换源代码

          1. 遍历文件中所有的 `i18n_pattern` 内容
          2. 找到每个内容对应的 i18n key
          3. 替换内容为 `[i18n_var_prefix].filename.keyname`
  4. 更新 i18n 文件

      1. 获取 `i18n_dir/main_file` 的内容，转换为一个 dict 对象 `in_obj`
      2. 将 `new_i18ns`合并到 `in_obj`中
      3. 将新的 i18n 对象写回到`i18n_dir/main_file`文件中。

### 案例

假设我正在开发一个 ts + svelte 的项目，我的项目的配置如下

```yaml
i18n_dir: src/i18n
main_file: zh_CN.yaml
code_files: ['*.ts', '*.svelte']
i18n_pattern: '\(\(`$1`\)\)'
dict:
  思源: SiYuan
strategy: diff
i18n_var_prefix: i18n
```

---

**i18n translate** 命令：

zh_CN.yaml 内容如下:

```yaml
main:
  title: 测试案例
  id: ID 号
hello: 你好
name: 名称
```

en_US.yaml 内容如下:

```yaml
main:
  title: Test sample
hello: Hello
```

发送了 GPT 翻译请求之后，新的 en_US.yaml 如下

```yaml
main:
  title: Test sample
  id: ID number
hello: Hello
name: Name
```

---

**i18n extract --dir ./src/components 命令**:

查找到了 info.ts 文件中有符合`i18n_pattern`的代码，如下:

```ts
showMessage(((`恭喜你已经成功上传`)))
ele.innerText = ((`取消上传`))
```

于是提取文本，汇总 lines 为

```ts
恭喜你已经成功上传
取消上传
```

gpt 返回结果为:

```json
{
  "uploadsucceed": "恭喜你已经成功上传",
  "cancelupload": "取消上传"
}
```

于是替换 info.ts 中的代码

```ts
showMessage(i18n.info.uploadsucceed)
ele.innerText = i18n.info.cancelupload
```

更新 zh_CN.yaml 为

```yaml
main:
  title: 测试案例
  id: ID 号
hello: 你好
name: 名称
info:
  uploadsucceed: 恭喜你已经成功上传
  cancelupload: 取消上传
```

### 要求

* 代码编写清晰，简明扼要
* 代码结构组织良好，做到高内聚低耦合；同时方便扩展
* 使用 python 编写；允许使用一些 cli 库来简化开发复杂度