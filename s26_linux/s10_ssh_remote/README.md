# s26-10: SSH 与远程操作

[← 返回概览](../README.md) | [上一章：包管理](../s09_package_mgmt/)

> *"怎么安全地连到远程服务器？怎么传文件？怎么配置免密登录？"*

---

## 问题 — 你的代码在云服务器上跑，你需要远程管理它

```bash
# 每次输入密码很烦
ssh user@my-server.com
user@my-server.com's password: _______

# 怎么传文件上去？
# 怎么在本地和服务器之间同步代码？
```

---

## 核心概念

### SSH — 加密的远程 Shell

```bash
ssh user@host           # 连接到远程主机
ssh -p 2222 user@host   # 指定端口（非 22）
ssh user@host command   # 在远程执行命令，不进入交互式 shell
```

SSH 做了两件事：
1. **加密** — 你和服务器之间的所有数据都是加密的
2. **认证** — 确认"你就是你"（密码或密钥）

### 密钥对认证（免密登录）

```
你的电脑                    远程服务器
    │                           │
    │  1. ssh-keygen 生成        │
    │     私钥: ~/.ssh/id_rsa    │
    │     公钥: ~/.ssh/id_rsa.pub│
    │                           │
    │  2. ssh-copy-id ─────────→│  把公钥放到 ~/.ssh/authorized_keys
    │                           │
    │  3. ssh user@host ──────→│  用私钥签名"我是xxx"
    │                           │  用公钥验证 → 通过! 免密登录
```

### SCP — 安全拷贝文件

```bash
scp file.txt user@host:/path/       # 本地上传
scp user@host:/path/file.txt ./     # 远程下载
scp -r project/ user@host:/path/    # 递归拷贝整个目录
```

### 端口转发 — 把远程端口"搬"到本地

```bash
# 远程的 5432 (PostgreSQL) 映射到本地的 5432
ssh -L 5432:localhost:5432 user@host

# 现在 localhost:5432 就是远程的 PostgreSQL!
```

---

## 跟 Agent 的关系

- s19 MCP 的远程传输可以用 SSH 隧道加密
- Agent 需要 `scp` 传文件到远程服务器
- 免密登录让 Agent 自动化成为可能

---

## 试一下

```bash
python s26_linux/s10_ssh_remote/code.py
```

---

## 小结

```
ssh user@host           远程登录
ssh-keygen              生成密钥对
ssh-copy-id             上传公钥 → 免密登录
scp                    安全拷贝文件
ssh -L 本地:远程:端口     端口转发
```
