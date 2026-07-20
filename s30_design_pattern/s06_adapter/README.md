# s30-06: 适配器 — 统一不同接口

[← 返回概览](../README.md) | [上一章：装饰器](../s05_decorator/) | [下一章：责任链](../s07_chain/)

> *"两个系统接口不兼容怎么对接？中间加一层适配器。"*

---

## 问题 — 你的代码期望统一接口，但对接的服务各不相同

```python
# Anthropic API: client.messages.create(model=..., messages=...)
# OpenAI API: client.chat.completions.create(model=..., messages=...)
# 两种不同的方法名和参数名!
```

---

## 方案：适配器统一

```python
class LLMAdapter(ABC):
    @abstractmethod
    def chat(self, messages): pass

class AnthropicAdapter(LLMAdapter):
    def chat(self, messages):
        return self.client.messages.create(...)  # 内部翻译

class OpenAIAdapter(LLMAdapter):
    def chat(self, messages):
        return self.client.chat.completions.create(...)  # 内部翻译
```

---

## Agent 中的应用

s19 MCP 协议适配——stdio/HTTP/SSE 三种传输方式，适配器统一为 MCP 标准接口。

---

## 试一下

```bash
python s30_design_pattern/s06_adapter/code.py
```
