# s26-06: 用户、组、sudo

[← 返回概览](../README.md) | [上一章：环境变量](../s05_env_config/) | [下一章：Shell 脚本](../s07_shell_scripting/)

> *"root 是什么？sudo 怎么工作的？为什么有些操作要加 sudo？"*

---

## 问题 — 你想安装一个包，系统说你不是 root

```bash
apt install nginx
# E: Could not open lock file /var/lib/dpkg/lock-frontend - open (13: Permission denied)
# E: Unable to acquire the dpkg frontend lock - are you root?
```

你需要 `sudo`。但为什么不是所有人都有权限？

---

## 原理：用户、组、root

```
root (UID=0)  →  工厂总管，所有区域的钥匙，什么都能做
普通用户       →  普通工人，只能进自己的区域
sudo           →  "总管的钥匙借我用一下"（临时提权）
```

### root 为什么特殊？

普通用户不能做的事（除非 root 或 sudo）：
- 绑定 1024 以下的端口（如 80、443）
- 修改系统文件（`/etc/`, `/usr/`）
- 安装/卸载软件
- 查看其他用户的文件

---

## 核心概念

### UID 和 GID

每个用户有一个 UID（用户ID）。root 的 UID 永远是 0。每个用户属于一个或多个组（GID）。

```bash
id                    # 查看当前用户的 UID、GID
whoami                # 我是谁
cat /etc/passwd       # 用户列表
cat /etc/group        # 组列表
```

### 文件属主

每个文件有属主（user）和属组（group）：

```bash
ls -l script.sh
# -rwxr-xr-x  1 alice  dev  1024  Jul 20 10:00  script.sh
#              ─┬──   ─┬─
#            属主(user) 属组(group)
```

### sudo 的原理

`sudo` = "substitute user do"（以另一个用户身份执行）

1. 你敲 `sudo apt install nginx`
2. sudo 检查 `/etc/sudoers` 里你有没有权限
3. 让你输密码确认
4. 以 root 身份执行 `apt install nginx`

---

## 试一下

```bash
python s26_linux/s06_users_perms/code.py
```

---

## 小结

```
root (UID=0)   系统总管，什么都能做
sudo           临时提权，以 root 身份执行一条命令
UID/GID        用户ID和组ID
/etc/passwd    用户列表
/etc/sudoers   谁可以用 sudo
```
