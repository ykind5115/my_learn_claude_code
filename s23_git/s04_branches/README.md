# s04: 分支 — 时间树的平行宇宙

[s03](../s03_staging_area/) → `s04` → [s05](../s05_merge/) → ... → s12
> *"分支不是复制代码。分支只是给一个 commit 贴了一张便利贴。"*
>
> **前提知识**: 做过多次 commit（s01），理解 HEAD 是什么（s02）。

---

## 1. 为什么需要分支？

假设你正在开发一个网站。main 分支上是稳定运行的版本。现在你要加一个「用户登录」功能。

**没有分支的世界**：
- 你在 main 上直接改代码
- 写到一半，线上出了个紧急 bug 要马上修
- 你的「半成品登录」和「bug 修复」混在一起
- 要么把半成品也发布（危险），要么手动备份半成品、回退、修 bug、再恢复半成品（痛苦）

**有分支的世界**：
```bash
git switch -c feature-login   # 创建分支，去那里开发登录功能
# 开发到一半，老板说线上有 bug
git switch main                # 切回 main
git switch -c hotfix-bug       # 创建 bug 修复分支
# 修完 bug，合并回 main
git switch main
git merge hotfix-bug
# 然后再切回 feature-login 继续开发
```

> **分支 = 互不干扰的平行工作空间。切换分支只需要几毫秒。**

---

## 2. 在时间树模型下理解分支

### 分支到底是什么？

**分支就是一个指向某个 commit 的指针。** 它只是一个文件（`.git/refs/heads/分支名`），里面写了一行 commit hash。

```
.git/refs/heads/main    →  内容是 "c3d4e5f..."  (一个 commit hash)
.git/refs/heads/feature →  内容是 "a1b2c3d..."  (另一个 commit hash)
```

### 时间树上的视角

```
    ○  commit A
    │
    ○  commit B  ← main（标签贴在 commit B 上）
    │
    ○  commit C  ← feature（标签贴在 commit C 上）
    │
    ●  commit D  ← HEAD → feature（HEAD 指向 feature，feature 指向 commit D）

当你站在 feature 分支上做 commit：
  - 新 commit D 的 parent = commit C
  - feature 标签自动移到 commit D
  - main 标签不动（还指着 commit B）
```

### 关键要点

- **创建分支** = 创建一个新指针，指向当前 commit（几毫秒，不复制文件）
- **切换分支** = 移动 HEAD，更新工作区文件为该分支指向的快照
- **在分支上 commit** = 新节点加入树，当前分支标签自动前移
- **其他分支不动** = 它们还指在原来的节点上

---

## 3. 分支操作详解

### 3.1 查看分支

```bash
git branch              # 列出所有本地分支，* 标记当前分支
git branch -a           # 包括远程分支
git branch -v           # 显示每个分支指向的 commit
```

### 3.2 创建分支

```bash
git branch feature-login              # 创建分支（但不切换过去）
git switch -c feature-login           # 创建 + 切换（推荐）
git checkout -b feature-login         # 同上（旧命令）
```

### 3.3 切换分支

```bash
git switch main                       # 切换到 main（推荐，Git 2.23+）
git checkout main                     # 切换到 main（旧命令）
```

**切换分支时 Git 做了什么？**
1. 把 HEAD 指向新分支
2. 把工作区所有文件替换为新分支指向的快照
3. 暂存区保持不变（如果有未提交的 add，会跟过去）

### 3.4 删除分支

```bash
git branch -d feature-login           # 安全删除（已合并的分支）
git branch -D feature-login           # 强制删除（未合并也删）
```

---

## 4. 分支策略入门

### 什么时候创建分支？

| 场景 | 分支命名示例 |
|------|-------------|
| 开发新功能 | `feature-login`, `feature-search` |
| 修复 bug | `fix-login-error`, `hotfix-security` |
| 实验 | `experiment-new-algo` |
| 发布准备 | `release-2.0` |

### 最基本的分支策略

```
main 分支:
  - 始终是可以部署的稳定版本
  - 不要直接在 main 上开发

feature 分支:
  - 从 main 分出
  - 开发完成后合并回 main
  - 合并后可以删除

    ○───○───○───○───●  ← main（稳定）
         └───○───○───┘  ← feature-login（开发完就删）
```

---

## 5. 常见错误（新手必读）

### ❌ 错误 1：在 main 上直接开发

```bash
git switch main
# 改代码...
git commit -m "新功能"   # ❌ 直接在 main 上 commit！
```

> **正确做法**：永远在 feature 分支上开发。
> ```bash
> git switch -c feature-xxx
> # 改代码...
> git commit -m "新功能"
> ```

### ❌ 错误 2：两个分支改了同一个文件，切换分支时报错

```bash
# 在 feature 分支上改了 app.py，但没 commit
git switch main
# error: Your local changes to the following files would be overwritten
```

> **解决**：要么 commit，要么 `git stash`（见 s10）

### ❌ 错误 3：分支名和 tag 名重复

```bash
git branch v1.0    # 创建了分支
git tag v1.0       # 又创建了同名的 tag → 冲突
```

> **规则**：分支名和 tag 名不要重复。

---

## 6. 你学到了什么

| 概念 | 一句话 |
|------|--------|
| 分支是什么 | 指向某个 commit 的「便利贴」 |
| 创建分支 | 只是创建一个新指针（不复制文件） |
| 切换分支 | HEAD 移动 + 工作区更新 |
| `git switch -c <name>` | 创建并切换到新分支 |
| `git branch` | 查看所有分支 |
| `git branch -d <name>` | 删除分支 |
| 分支策略 | main = 稳定版，feature 分支 = 开发中 |

---

## 7. 自己动手

1. **在你的学习仓库里**：创建 3 个分支（不合并），在每个分支上做 1-2 个 commit
2. **用 `git log --graph --all --oneline`** 观察分支结构
3. **切换分支**：`git switch main`，看工作区文件变回去了吗？
4. **在 main 和 feature 上分别改同一个文件**，尝试不 commit 就切换——看 Git 报什么错
5. **删除一个已合并的分支**，再尝试删除一个未合并的分支——看提示有什么不同

---

> **下一章：[s05: 合并](../s05_merge/)** — 把两条时间线汇合到一起
