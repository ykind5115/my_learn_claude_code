# s30-01: 单例 — 全局唯一实例

[← 返回概览](../README.md) | [下一章：工厂](../s02_factory/)

> *"怎么保证一个类在整个程序里只有一个实例？"*

---

## 问题 — Logger、Config、DB 连接，全局只需要一个

你不想每次都 `Config()` 创建新配置对象。你希望整个程序共享同一个实例。

---

## 方案：3 种 Python 写法

### 1. `__new__` 控制

```python
class Singleton:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 2. 模块级单例（Python 最自然的方式）

```python
# config.py
class Config:
    def __init__(self):
        self.api_key = "..."

config = Config()  # 模块顶层创建 → import 自动唯一
```

### 3. 装饰器单例

```python
def singleton(cls):
    instances = {}
    def get():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get
```

---

## Agent 中的应用

s09 Memory 系统——整个 Agent 只需要一个 Memory 实例管理所有记忆。

---

## 试一下

```bash
python s30_design_pattern/s01_singleton/code.py
```
