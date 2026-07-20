# s30-07: 责任链 — 请求沿链传递

[← 返回概览](../README.md) | [上一章：适配器](../s06_adapter/) | [下一章：命令](../s08_command/)

> *"一个请求要经过多层处理，每层可以批准、拒绝或传递。怎么优雅实现？"*

---

## 问题 — 审批流程：组长→经理→总监

每个请求要经过多层审批，每层逻辑独立，层数可能变化。if/else 嵌套很难维护。

---

## 方案：链式传递

```python
class Handler:
    def __init__(self):
        self._next = None
    def set_next(self, handler):
        self._next = handler
        return handler
    def handle(self, request):
        if self._next:
            return self._next.handle(request)
        return "无人处理"
```

---

## Agent 中的应用

s03 权限系统——权限检查链：`allow 列表 → deny 列表 → 询问用户`，每层可以拦截或放行。

---

## 试一下

```bash
python s30_design_pattern/s07_chain/code.py
```
