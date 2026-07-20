# s30-03: 策略 — 运行时切换算法

[← 返回概览](../README.md) | [上一章：工厂](../s02_factory/) | [下一章：观察者](../s04_observer/)

> *"怎么在运行时切换不同的算法/行为，而不改调用方代码？"*

---

## 问题 — if/else 选择不同算法

```python
def compress(data, method):
    if method == "gzip":
        return gzip_compress(data)
    elif method == "lz4":
        return lz4_compress(data)
    # 每加一种压缩算法就要改 compress()
```

---

## 方案：策略接口 + 具体策略

```python
class CompressStrategy:
    def compress(self, data): raise NotImplementedError

class GzipCompress(CompressStrategy):
    def compress(self, data): ...

class Lz4Compress(CompressStrategy):
    def compress(self, data): ...

# 使用时注入策略
def process(data, strategy: CompressStrategy):
    return strategy.compress(data)
```

---

## Agent 中的应用

s08 Context Compaction——不同压缩策略（摘要/截断/滑动窗口）可在运行时切换。

---

## 试一下

```bash
python s30_design_pattern/s03_strategy/code.py
```
