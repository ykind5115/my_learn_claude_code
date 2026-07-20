# s00-07: Shell、JSON、YAML

[← 返回概览](../README.md) | [上一章：协程](../06_coroutine/) | [下一章：HTTP/网络](../08_http_network/)

> *Shell 是模型的"手"，JSON 是 Agent 世界的"通用语"，YAML 是人类友好的配置方式。这三个是你读 s01 代码时每行都会碰到的。*

---

## 问题 — Agent 用什么语言跟你和世界对话？

- **跟你（人类）**：Markdown — 你现在读的东西
- **跟系统（OS）**：Shell 命令 — `ls`, `cat`, `python ...`
- **跟 API（机器）**：JSON — `{"tool": "bash", "args": {...}}`
- **跟你（配置）**：YAML — CLAUDE.md 的 frontmatter

---

## 核心概念

### 1. Shell — 工头

s01 里模型调用的第一个工具是 `bash`。它会生成类似这样的命令：

```bash
ls -la
find . -name "*.py"
cat README.md | grep error
```

**核心语法速查**：

| 语法 | 含义 | 示例 |
|------|------|------|
| `\|` | 管道: stdout → stdin | `cat f \| grep err` |
| `>` | 覆盖写入文件 | `echo hi > f.txt` |
| `>>` | 追加写入 | `echo hi >> log` |
| `2>&1` | stderr 并入 stdout | `python x.py 2>&1` |
| `*` `**` | 通配符 | `*.py` |
| `$(cmd)` | 命令替换 | `echo $(date)` |
| `&&` | 前成功才跑后 | `make && ./app` |

**shell=True 安全警告**：永远不要对用户输入用 `shell=True`。如果用户输入 `"; rm -rf /`，你就在执行 `echo ""; rm -rf /`。

### 2. JSON — Agent 通用语

```json
{
  "name": "bash",
  "description": "Run a shell command",
  "input_schema": {
    "type": "object",
    "properties": {
      "command": {"type": "string", "description": "The command"}
    },
    "required": ["command"]
  }
}
```

这就是 s01 里的工具定义。六个类型走天下：`string` `number` `boolean` `null` `object` `array`。

**JSON Schema** 是 JSON 的"类型标注"——告诉模型"这个字段是 string、这两个必填"。

### 3. YAML — 人写的 JSON

```yaml
# JSON 版本:
# {"name": "bash", "input_schema": {"type": "object"}}

# YAML 版本:
name: bash
input_schema:
  type: object
```

YAML 用缩进代替大括号，适合手写。s07 的技能清单、CLAUDE.md 的 frontmatter 都是 YAML。

---

## 跟 Agent 的关系

| 章节 | 数据格式 |
|------|---------|
| **s01** | 工具定义用 JSON Schema，模型调 bash 命令 |
| **s02** | 更多工具，参数都用 JSON Schema 定义 |
| **s07** | 技能清单是 YAML 格式 |

---

## 试一下

```bash
python 07_shell_json/code.py
```

---

## 小结

```
Shell: 模型的"手"，执行 bash 命令
JSON:  模型的"语言"，API 通信和工具定义
YAML:  人类的"便利"，配置文件和清单
```
