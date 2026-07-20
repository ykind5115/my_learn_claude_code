# s26-05: 环境变量与 Shell 配置

[← 返回概览](../README.md) | [上一章：进程管理](../s04_process/) | [下一章：用户与权限](../s06_users_perms/)

> *".bashrc、.profile、.env、export、source……这些到底有什么区别？Agent 的 API Key 是怎么传到子进程的？"*

---

## 问题 — 你配了一个环境变量，重启终端就没了

```bash
export MY_KEY="abc123"
echo $MY_KEY    # abc123

# 关闭终端，重新打开
echo $MY_KEY    # (空)
```

环境变量的作用域是**进程**。`export` 让子进程能看到，但不会永久保存。

---

## 原理：公告板

环境变量 = 工厂公告板上的便条。每个工人（进程）出生时继承父进程的公告板。

```
Shell 进程 (登录时启动)
  ├── env: PATH=/usr/bin, HOME=/home/me
  │
  ├── 你 export MY_KEY=abc → 公告板新增 MY_KEY
  │
  ├── 启动子进程 python app.py
  │     └── 继承公告板: PATH + HOME + MY_KEY ✓
  │
  └── 启动另一个子进程
        └── env={"PATH": "/usr/bin"} (只用 PATH)
              └── MY_KEY → 不存在 ✗
```

---

## 核心概念

### 配置文件的加载顺序

```
登录 Shell (你打开终端):
  1. /etc/profile           (系统级，全局)
  2. ~/.bash_profile        (用户级，只加载一次)
     └── 如果没有 → ~/.bash_login → ~/.profile

非登录 Shell (脚本、子 shell):
  1. ~/.bashrc              (每次打开都加载)

所以你通常在 ~/.bashrc 里配 alias 和 PATH。
```

### .env 文件不是 Linux 原生的

`.env` 是应用程序约定（Node.js 的 dotenv、Python 的 python-dotenv），Linux 内核不认它。但效果一样——`load_dotenv()` 把文件内容读到 `os.environ`。

### 查看和设置

```bash
env              # 查看所有环境变量
echo $HOME       # 查看单个
export VAR=val   # 设置（对本进程和子进程可见）
VAR=val          # 设置（只对本进程可见，子进程看不到）
```

---

## 试一下

```bash
python s26_linux/s05_env_config/code.py
```

---

## 小结

```
export VAR=val    对当前进程和子进程都可见
VAR=val           只对当前进程可见
source file       把文件里的命令在当前 shell 里执行
启动文件:
  登录: /etc/profile → ~/.bash_profile
  非登录: ~/.bashrc
.env              应用约定，load_dotenv() 读到 os.environ
```
