# s26-03: 管道与重定向

[← 返回概览](../README.md) | [上一章：文件操作与权限](../s02_file_ops/) | [下一章：进程管理](../s04_process/)

> *"| > >> 2>&1 到底在干什么？为什么 Agent 要把 stdout 和 stderr 合并？"*

---

## 问题 — 你写了一个脚本，输出和报错混在一起

```bash
python my_script.py > output.txt
# 输出到了 output.txt，但报错还在屏幕上刷屏
```

你需要把 stdout 和 stderr 分开（或合并）——这就是重定向的作用。

---

## 原理：每个进程有三根"管子"

s00 里讲过工厂比喻——每个工人有三根管子：

```
         ┌──────────────┐
stdin  → │   进程(工人)   │ → stdout (fd 1, 正常输出)
(fd 0)   │              │ → stderr (fd 2, 错误输出)
         └──────────────┘
```

默认情况下，stdin 接键盘，stdout 和 stderr 都接屏幕。重定向就是**把这些管子接到别的地方**。

---

## 核心概念

### 重定向速查表

| 写法 | 含义 | 工厂比喻 |
|------|------|---------|
| `cmd > file` | stdout 写到文件（覆盖） | 出货口对准箱子 |
| `cmd >> file` | stdout 写到文件（追加） | 出货口对准箱子，不扔旧东西 |
| `cmd < file` | 从文件读入 stdin | 进料口接箱子 |
| `cmd 2> file` | stderr 写到文件 | 废料口对准垃圾桶 |
| `cmd 2>&1` | stderr 合并到 stdout | 废料口并入出货口 |
| `cmd &> file` | stdout + stderr 都写到文件 | 两个口都对准同一个箱子 |

### 管道 `|` — 传送带

```bash
cat access.log | grep "ERROR" | wc -l
```

分解：
1. `cat access.log` → stdout = 整个日志文件的内容
2. `|` → 把 stdout 接到 grep 的 stdin
3. `grep "ERROR"` → 只留含 ERROR 的行 → stdout
4. `|` → 把 stdout 接到 wc 的 stdin
5. `wc -l` → 数有多少行 → stdout

**所有进程同时运行！** 不是"等 cat 跑完再 grep"——管道让它们并行工作，数据像在传送带上流动。

### 为什么要 `2>&1`？

这是 s01 Agent 循环里最关键的操作：

```python
out = (r.stdout + r.stderr).strip()
```

Agent 需要看到命令的**完整输出**——成功的结果和失败的错误都要。如果 stdout 和 stderr 分开处理，错误信息就丢了。

---

## 试一下

```bash
python s26_linux/s03_pipes_redirect/code.py
```

---

## 小结

```
> file     stdout → 文件 (覆盖)
>> file    stdout → 文件 (追加)
2> file    stderr → 文件
2>&1      stderr → 并入 stdout
|          stdout → 下一个进程的 stdin

管道 = 传送带: 所有进程并行运行，数据流动
```
