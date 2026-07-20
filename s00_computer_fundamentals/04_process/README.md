# s00-04: 进程

[← 返回概览](../README.md) | [下一章：线程](../05_thread/)

> *进程 = 一个正在运行的程序。每个进程有自己的 PID、内存空间和三根"传送带"（stdin/stdout/stderr）。*

---

## 问题 — 为什么需要理解进程？

s01 的第一行工具代码是 `subprocess.run(command, shell=True)`。Agent 不是自己动手干活——它**创建子进程**来执行命令。不理解进程，就不理解 Agent 是怎么"做事"的。

---

## 原理

```
Shell (父进程)
    │
    │  fork() — 克隆自己
    │
    ├─→ 子进程 (PID: 新分配的)
    │      │
    │      │  exec() — 用新程序覆盖自己
    │      │
    │      ▼
    │   执行 ls / cat / python ...
    │      │
    │      │  exit(0) 或 exit(非0)
    │      ▼
    │   子进程消失
    │
    │  waitpid() — 父进程收尸，拿到退出码
    ▼
继续运行
```

**fork + exec + waitpid** 是进程管理的三剑客。

---

## 核心概念

### 1. 每个进程有三根"传送带"

```
stdin  (fd 0) — 输入   — 程序读数据的地方（默认接键盘）
stdout (fd 1) — 输出   — 正常结果走这里（默认接屏幕）
stderr (fd 2) — 错误   — 报错走这里（默认也接屏幕，但独立于 stdout）
```

`s01` 里这行代码的意义：

```python
out = (r.stdout + r.stderr).strip()
```

**合并 stdout 和 stderr**——因为模型需要看到完整输出。如果你只读 stdout，`ls /nonexistent` 的报错就丢了，模型不知道发生了什么。

### 2. 退出码 = 成功还是失败？

```bash
echo "hello"       # 退出码 0  → 成功
ls /nonexistent    # 退出码 2  → 失败
```

- **0 = 成功**
- **非 0 = 失败**（不同数字代表不同错误类型）

真正的 Claude Code 会检查退出码：非零就把错误喂回模型让它重试。这就是 s11 错误恢复的基础。

### 3. 环境变量 = 全局配置

```python
MODEL = os.environ["MODEL_ID"]  # 读环境变量
```

`.env` 文件 → `load_dotenv()` → `os.environ`。API Key、模型名、调试开关都走这条路。子进程自动继承父进程的所有环境变量。

### 4. CWD = 当前工作目录

每个进程有一个 `cwd`（当前在哪）。你 `cd /tmp`，就是在改当前 Shell 进程的 `cwd`。子进程继承父进程的 `cwd`。

```python
import os
print(os.getcwd())  # → 这个进程的当前目录
```

### 5. 进程隔离

每个进程有独立的内存地址空间。进程 A 崩了不会影响进程 B。这就是 s06 subagent 用独立进程的原因——它挂了不影响主 Agent。

---

## 跟 Agent 的关系

| 章节 | 怎么用的 |
|------|---------|
| **s01** | `subprocess.run()` 创建子进程执行 bash 命令 |
| **s03** | 权限系统决定哪些子进程可以创建 |
| **s06** | subagent 跑在独立进程里（隔离 + 安全） |
| **s13** | 后台任务用子进程执行耗时操作 |
| **s18** | 工作树隔离 = 进程级别的工作区分离 |

---

## 试一下

```bash
python 04_process/code.py
```

观察：
- 子进程的 PID 和父进程不同
- stdout 和 stderr 是分开捕获的
- 退出码怎么判断成功/失败

---

## 小结

```
进程 = fork() 克隆 + exec() 变身 + waitpid() 收尸
       ↓
每个进程自带: stdin(0) stdout(1) stderr(2)
       ↓
子进程继承: 环境变量 + CWD
       ↓
退出码: 0=成功，非0=失败
```
