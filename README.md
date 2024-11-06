# benchmark-result-analyze

```bash
python benchmark.py \
--api-url http://127.0.0.1:11434/v1 \
--model qwen2.5-coder:7b-instruct \
--mermaid-optimize true \
--mermaid-file mermaid\mermaids.jsonl \
--benchmark MultiPL-E \
--language cpp \
--output-folder tutorial 
```


## 生成结果

| 参数名              | 类型   | 值                         | 描述                         |
|------------------|------|---------------------------|----------------------------|
| api-url          | str  | http://127.0.0.1:11434/v1 | ollama部署的 api，端口默认为 11434  |
| model            | str  | qwen2.5-coder:7b-instruct | 模型名称,以 ollama 里的模型名为准      |
| mermaid-optimize | bool | true                      | 是否使用 mermaid 优化            |
| mermaid-file     | str  | mermaid/mermaids.jsonl    | mermaid 文件路径，用于优化          |
| benchmark        | str  | MultiPL-E / HumanEval     | benchmark 名称，用于生成结果,只有两种可选 |
| language         | str  | cpp                       | 生成的代码语言                    |
| output-folder    | str  | tutorial                  | 生成的结果文件夹                   |

### 可选

| 参数名         | 类型    | 默认值  | 描述          |
|-------------|-------|------|-------------|
| temperature | float | 0.2  | 模型温度值       |
| top-p       | float | 0.95 | top-p值      |
| max-token   | int   | 1024 | 最大 token 数量 |
| k           | int   | 1    | 每个问题生成结果数   |

在运行完成后在output-folder文件夹下会生成结果和代码抽取前后对比的 json 文件。
如果是 MultiPL-E，则会生成 MultiPL-E_{语言}_[mermaid_optimize]_{时间戳} 的文件夹，里面包含了每个问题的结果的 jsonl.gz文件。
然后按照 MultiPL-E 官方评估结果的[步骤](https://nuprl.github.io/MultiPL-E/tutorial.html#execution)进行即可。

如果是 Humaneval, 则会在 output-folder 目录下生成 samples.jsonl。
然后运行 `evaluate_functional_correctness samples.jsonl`,需要安装了human-eval的 pip 包。

## 分析结果

```bash
python analyze.py \
--batch 1 \
--benchmark MultiPL-E \
--input tutorial/MultiPL-E_{语言}_[mermaid_optimize]_{时间戳} \
--output-dir output
```

| 参数名        | 类型  | 默认值    | 描述                                            |
|------------|-----|--------|-----------------------------------------------|
| batch      | int | 1      | 每个问题生成结果数                                     |
| benchmark  | str | 无      | multiple / humaneval                          |
| input      | str | 无      | 输入文件，如果是 humaneval 则是 jsonl 文件，multiple 则是文件夹 |
| output-dir | str | output | 结果保存目录                                        |