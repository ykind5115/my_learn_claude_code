# s30-04: 观察者 — 事件通知

[← 返回概览](../README.md) | [上一章：策略](../s03_strategy/) | [下一章：装饰器](../s05_decorator/)

> *"状态变了，怎么自动通知所有关心的对象？"*

---

## 问题 — 订单状态变了，库存、物流、通知都要知道

把通知逻辑硬编码在订单类里 → 每加一个通知方就要改订单类。

---

## 方案：发布-订阅

```python
class EventBus:
    def __init__(self):
        self._handlers = {}
    def on(self, event, handler):
        self._handlers.setdefault(event, []).append(handler)
    def emit(self, event, data):
        for h in self._handlers.get(event, []):
            h(data)
```

---

## Agent 中的应用

s04 Hooks 系统——事件发生时触发注册的回调（`on_tool_start`、`on_stop` 等）。

---

## 试一下

```bash
python s30_design_pattern/s04_observer/code.py
```
