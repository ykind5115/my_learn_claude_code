# s07: 远程仓库 — 把你的时间树分享给别人

[s06](../s06_conflicts/) → `s07` → [s08](../s08_collaboration/) → ... → s12
> *"远程仓库就是另一台电脑上的另一棵时间树。push = 把我的节点发过去，pull = 把别人的节点拿过来。"*
>
> **前提知识**: 会 commit（s01）、分支（s04）、合并（s05）。有一个 GitHub 账号（注册免费）。

---

## 1. 为什么需要远程仓库？

到目前为止，你的时间树只存在于你自己的电脑上。

**问题来了**：
- 你的队友怎么拿到你的代码？
- 你的硬盘坏了，代码还在吗？
- 你怎么把代码部署到服务器上？

**远程仓库 = 存在另一台电脑（通常是 GitHub 服务器）上的时间树副本。**

```
你的电脑                       GitHub                      队友的电脑
┌──────────┐    git push     ┌──────────┐    git pull     ┌──────────┐
│ 本地仓库  │ ──────────────→ │ 远程仓库  │ ←────────────── │ 本地仓库  │
│          │ ←────────────── │ (GitHub) │ ──────────────→ │          │
│ 时间树 A  │    git pull     │ 时间树 B  │    git push     │ 时间树 C  │
└──────────┘                └──────────┘                └──────────┘
```

> 每个人电脑上都有完整的、独立的时间树。远程仓库只是另一个副本，没有「主/从」关系。

---

## 2. 在时间树模型下理解远程操作

### 远程分支 vs 本地分支

```
本地仓库中:
  main                 ← 你的本地 main 分支
  origin/main          ← 你上次看到的「远程 main」的镜像（只读）
  origin/feature-xxx   ← 你上次看到的「远程 feature-xxx」的镜像

远程仓库中（GitHub 上）:
  main                 ← 真正的远程 main
  feature-xxx          ← 真正的远程 feature-xxx
```

> `origin/main` 是你本地的一个「只读指针」——它记录了你上次和远程同步时，远程的 main 指在哪个 commit。它不是自动更新的。

### push：把你的节点发给远程

```
push 之前:
  本地:  ○───○───●  ← main (HEAD)
  远程:  ○───○      ← main

git push:
  本地:  ○───○───●  ← main (HEAD), origin/main
  远程:  ○───○───●  ← main

push 做了两件事:
  1. 把本地的新节点（●）上传到远程
  2. 把远程的 main 标签移到 ●（和本地对齐）
```

### fetch：看看远程有什么新节点

```
fetch 之前:
  本地:  ○───○      ← main, origin/main
  远程:  ○───○───●  ← main（队友推送了新节点）

git fetch:
  本地:  ○───○      ← main
         ○───○───●  ← origin/main（更新了）
  远程:  ○───○───●  ← main（没变）

fetch 只更新本地的 origin/* 指针，不改变你的本地分支和工作区。
```

### pull = fetch + merge

```
git pull = git fetch + git merge origin/main

pull 做了:
  1. fetch: 下载远程的新节点
  2. merge: 把 origin/main 合并到本地 main
```

---

## 3. 核心命令详解

### 3.1 `git clone` — 复制整棵時間树

```bash
git clone https://github.com/user/repo.git
# 或
git clone git@github.com:user/repo.git
```

**发生了什么？**
1. 在 GitHub 上创建远程仓库（或者 clone 已有仓库）
2. 本地创建一个新目录
3. 把远程的整棵时间树下载下来
4. 自动设置 `origin` 指向远程地址
5. 自动 checkout main 分支

### 3.2 `git remote` — 管理远程地址簿

```bash
git remote -v              # 查看所有远程仓库地址
git remote add <名字> <URL> # 添加一个远程仓库
git remote remove <名字>   # 删除
```

> `origin` 只是一个约定俗成的名字——你 clone 时 Git 自动起的。可以改，可以有多个 remote。

### 3.3 `git push` — 把你的节点推上去

```bash
git push origin main                    # 把本地 main 推送到 origin 的 main
git push -u origin main                 # 推送 + 设置上游（以后直接 git push）
git push origin feature-login           # 推送 feature 分支
```

### 3.4 `git fetch` — 看看远程有什么新东西

```bash
git fetch                               # 下载所有远程分支的更新（不合并）
git fetch origin                        # 指定 remote
git log --oneline origin/main           # 查看远程 main 的最新 commit
```

### 3.5 `git pull` — 拿来并合并

```bash
git pull                                # = fetch + merge
git pull --rebase                       # = fetch + rebase（见 s09）
```

---

## 4. 首次 push 的完整流程

```bash
# 1. 在 GitHub 上创建仓库（不要勾选"Initialize with README"）

# 2. 在本地:
git init
git add .
git commit -m "首次提交"

# 3. 关联远程仓库:
git remote add origin https://github.com/你的用户名/仓库名.git

# 4. 推送:
git push -u origin main
# -u = --set-upstream，以后只需 git push 即可
```

---

## 5. 常见错误（新手必读）

### ❌ 错误 1：push 被拒绝——远程有本地没有的 commit

```bash
git push
# ! [rejected] main -> main (fetch first)
# 原因: 队友推了新 commit，你的本地落后了
```

> **修复**：先 `git pull`（或 `git pull --rebase`），解决可能的冲突，再 push。

### ❌ 错误 2：pull 时出现合并冲突

```bash
git pull
# CONFLICT (content): Merge conflict in app.py
```

> 和 s06 中讲的一样——手动解决冲突，`git add`，`git commit`。

### ❌ 错误 3：push 了不该 push 的东西

```bash
git push          # 把 node_modules/ 也推上去了！
```

> **预防**：用 `.gitignore` 文件排除不需要版本控制的文件和目录。

---

## 6. .gitignore — 告诉 Git 忽略什么

```gitignore
# 依赖
node_modules/
venv/
__pycache__/

# 密钥
.env
*.pem

# IDE
.vscode/
.idea/

# 系统文件
.DS_Store
Thumbs.db
```

---

## 7. 你学到了什么

| 概念 | 一句话 |
|------|--------|
| Remote | 另一台电脑上的时间树副本 |
| `origin/main` | 本地存储的「远程 main 镜像」指针 |
| `git push` | 把本地新节点上传到远程 |
| `git fetch` | 下载远程新节点（但不合并） |
| `git pull` | fetch + merge |
| `git clone` | 复制整棵时间树到本地 |
| `.gitignore` | 告诉 Git 哪些文件不用管 |

---

## 8. 自己动手

1. **在 GitHub 上创建一个仓库**，把学习项目 push 上去
2. **push 后再做一个本地 commit**，然后 push——看是否只需要 `git push`
3. **手动在 GitHub 上编辑一个文件**（模拟队友的操作），然后 `git fetch` + `git log origin/main`——看远程的改动是否出现在本地
4. **`git pull`** 把 GitHub 上的改动拉下来
5. **创建一个 `.gitignore`** 文件，排除 `*.log` 和 `temp/`

---

> **下一章：[s08: 协作工作流](../s08_collaboration/)** — 团队的标准化协作方式
