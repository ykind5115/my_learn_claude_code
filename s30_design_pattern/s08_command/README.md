# s30-08: 命令 — 把操作封装成对象

[← 返回概览](../README.md) | [上一章：责任链](../s07_chain/)

> *"怎么把操作封装成对象，支持撤销、重做、排队？"*

---

## 问题 — 编辑器要支持 undo/redo

每步操作（插入、删除、替换）要能撤销。直接在代码里改状态，没法回溯。

---

## 方案：命令对象

```python
class Command(ABC):
    @abstractmethod
    def execute(self): pass
    @abstractmethod
    def undo(self): pass

class InsertCommand(Command):
    def __init__(self, doc, text, pos):
        self.doc = doc; self.text = text; self.pos = pos
    def execute(self):
        self.doc.insert(self.pos, self.text)
    def undo(self):
        self.doc.delete(self.pos, len(self.text))
```

---

## Agent 中的应用

s12 Task System——每个任务是一个命令对象，支持执行、回滚、重试。

---

## 试一下

```bash
python s30_design_pattern/s08_command/code.py
```
