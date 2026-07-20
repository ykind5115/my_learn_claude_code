# s30-05: 装饰器 — 不修改原函数加功能

[← 返回概览](../README.md) | [上一章：观察者](../s04_observer/) | [下一章：适配器](../s06_adapter/)

> *"怎么给函数加日志、计时、权限检查，而不改函数本身的代码？"*

---

## 问题 — 每个函数都要加 `print('开始')` `print('结束')`

复制粘贴几百次。要改日志格式？几百处一起改。

---

## 方案：Python @ 装饰器

```python
def log(func):
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}")
        result = func(*args, **kwargs)
        print(f"完成 {func.__name__}")
        return result
    return wrapper

@log
def greet(name):
    return f"Hello, {name}"
```

---

## Agent 中的应用

`s02` 的 `@tool` 装饰器——把普通 Python 函数注册为 Agent 可调用的工具。

---

## 试一下

```bash
python s30_design_pattern/s05_decorator/code.py
```
