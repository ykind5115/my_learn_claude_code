# s26: Linux 基础 — 把操作系统装进工具箱

[中文](README.md)

> *"Linux 不是一个神秘的黑盒。Linux 是一个进程工厂——你告诉工头(Shell)要做什么，工头去调度工人(进程)。"*
>
> 本课程面向 **Linux 零基础**的学习者。不假设你用过任何命令行。
> 每一章只比上一章多一个概念，每一步都用「进程工厂」模型来解释「为什么」。
> 最终目标是：学完能理解 **Agent 在 Linux 上到底是怎么跑的**，而且**真正理解每个命令在做什么**。

---

## 为什么大多数 Linux 教程让人学不会？

大多数教程上来就让你背命令：`ls`、`cd`、`chmod`、`ps`、`grep`……几百个命令堆在一起，没有主线，学完就忘。

问题在于：**命令是"怎么用"，不是"为什么"**。不知道 Linux 的设计哲学，你永远在死记硬背。

**本课程反其道而行之**：先用 s00 帮你建立一张「进程工厂」的地图——**Everything is a file**。之后每一章都从这个模型出发，让你知道这个命令在工厂的哪个位置、解决什么问题。

---

## 开始之前：你需要什么基础？

- Python 基础（会写函数、会用 `subprocess` 更好但不必须）
- 一个能敲命令的终端（Git Bash / WSL / Linux / macOS 都行）
- 想理解 Agent 底层是怎么运作的好奇心

> 从 [s00](s00_mental_model/) 开始 — 纯概念，不敲命令，帮你建立心智模型。

---

## 学习路线图

```
s00  心智模型：进程工厂          ← 纯概念，建立地图
 │
s01  文件系统层次结构             ← "文件都在哪？"
 │
s02  文件操作与权限               ← "为什么 Permission denied？"
 │
s03  管道与重定向                 ← "| > 2>&1 到底在干什么？"
 │
s04  进程管理                     ← "怎么查看、停止进程？"
 │
s05  环境变量与配置               ← ".bashrc 和 .env 怎么工作？"
 │
s06  用户、组、sudo              ← "root 是什么？"
 │
s07  Shell 脚本                   ← "怎么把命令串成自动化？"
 │
s08  文本处理 (grep/sed/awk)     ← "怎么从日志里捞信息？"
 │
s09  包管理                       ← "apt install 背后发生了什么？"
 │
s10  SSH 与远程操作               ← "怎么连到远程服务器？"
```

---

## 模块总览

### 🧭 第 0 章：心智模型

| # | 模块 | 要解决的问题 | 不写代码 |
|---|------|-------------|---------|
| s00 | [进程工厂](s00_mental_model/) | "Linux 到底是什么？怎么理解它？" | ✅ |

### 📁 第 1 章：文件系统

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s01 | [文件系统层次结构](s01_filesystem/) | "文件都在哪？/etc /var /tmp 是干什么的？" | FHS, /proc, 目录树 |
| s02 | [文件操作与权限](s02_file_ops/) | "为什么 Permission denied？" | rwx, chmod, chown, inode |
| s03 | [管道与重定向](s03_pipes_redirect/) | "\| > 2>&1 到底在干什么？" | stdin/stdout/stderr, pipe, tee |

### ⚙️ 第 2 章：进程与系统

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s04 | [进程管理](s04_process/) | "怎么查看、停止、后台运行进程？" | ps, kill, fg/bg, 僵尸进程 |
| s05 | [环境变量与配置](s05_env_config/) | ".bashrc .profile .env 有什么区别？" | env, export, source, 启动文件 |
| s06 | [用户与权限](s06_users_perms/) | "root 是什么？sudo 怎么工作？" | UID/GID, passwd, sudo, 文件属主 |

### 🔧 第 3 章：自动化与运维

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s07 | [Shell 脚本](s07_shell_scripting/) | "怎么把命令串成自动化脚本？" | 变量, if/for, 退出码, shebang |
| s08 | [文本处理](s08_text_processing/) | "grep sed awk 怎么用？" | 正则, 管道过滤, 列提取 |
| s09 | [包管理](s09_package_mgmt/) | "apt install 背后发生了什么？" | 依赖, 源, 版本锁定 |
| s10 | [SSH 远程](s10_ssh_remote/) | "怎么连到远程服务器？免密登录？" | 密钥对, scp, 端口转发 |

---

## 如何使用本课程

### 学习节奏

每个模块按这个顺序：

1. **读 README 的「问题」部分** — 理解这个模块要解决什么痛点
2. **读 README 的「原理」部分** — 用"进程工厂"的比喻理解核心概念
3. **运行 code.py** — 在终端里看实际效果
4. **自己动手复现** — 跟着输出，在自己的环境里敲一遍命令
5. **做「自己动手」练习** — 每个模块末尾有练习
6. **再读一遍 README** — 此时有些概念你会理解得更深

### 不要跳章

每个模块的概念都依赖前一个模块。跳着学 = 浪费时间。

### 关于平台

本课程设计为在 **Git Bash**（Windows）或任何 Unix 终端上运行。code.py 通过 Python 的 `subprocess` 调用命令，跨平台兼容。

---

## 快速开始

```bash
# 1. 从概念章开始（纯阅读）
# 打开 s26_linux/s00_mental_model/README.md

# 2. 运行第一个演示
python s26_linux/s01_filesystem/code.py

# 3. 按顺序学习
python s26_linux/s02_file_ops/code.py
python s26_linux/s03_pipes_redirect/code.py
# ...
```

---

## 跟 Agent 的关系

| Linux 概念 | Agent 章节 | 怎么用的 |
|-----------|-----------|---------|
| stdin/stdout/stderr + 管道 | s01 Agent Loop | subprocess.run() 捕获工具输出 |
| 文件权限 (rwx) | s03 权限系统 | 防止 Agent 越权访问文件 |
| 进程管理 (ps/kill/signals) | s01, s13 | 创建子进程、超时杀进程、后台任务 |
| 环境变量 | s01 | .env → os.environ → API Key |
| 文本处理 (grep) | s02 | 搜索工具输出中的关键信息 |
| SSH | s19 MCP | 远程 Agent 通信 |

---

## 和 learn-claude-code 项目的关系

| learn-claude-code | s26_linux |
|---|---|
| Agent Loop = 一切的基础 | Everything is a file = 一切的基础 |
| 渐进式添加工具 (s01→s20) | 渐进式添加 Linux 能力 (s01→s10) |
| 每章一个可运行的 Agent | 每章一个可运行的 Python 演示 |
| Harness 层的概念 | OS 层的概念 |
| 从简单到复杂，不跳步 | 从简单到复杂，不跳步 |
