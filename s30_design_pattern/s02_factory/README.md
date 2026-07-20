# s30-02: 工厂 — 按需创建对象

[← 返回概览](../README.md) | [上一章：单例](../s01_singleton/) | [下一章：策略](../s03_strategy/)

> *"怎么根据参数创建不同类型的对象，而不让调用方知道具体类？"*

---

## 问题 — if/elif 散落各处创建不同子类

```python
if tool_name == "bash":
    return BashTool()
elif tool_name == "read":
    return ReadTool()
elif tool_name == "write":
    return WriteTool()
# 每加一个新工具, 到处都要改!
```

---

## 方案：工厂集中创建

```python
class ToolFactory:
    _tools = {}
    @classmethod
    def register(cls, name, tool_cls):
        cls._tools[name] = tool_cls
    @classmethod
    def create(cls, name):
        return cls._tools[name]()

# 注册
ToolFactory.register("bash", BashTool)
ToolFactory.register("read", ReadTool)
# 使用
tool = ToolFactory.create("bash")  # 返回 BashTool 实例
```

---

## Agent 中的应用

s02 Tool Use——根据模型返回的 `tool_use.name` 字符串，工厂创建对应的工具处理器。

---

## 试一下

```bash
python s30_design_pattern/s02_factory/code.py
```
