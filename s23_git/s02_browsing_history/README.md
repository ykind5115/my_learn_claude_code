# s02: 浏览历史 — 在时间树上自由跳转

[s01](../s01_first_commit/) → `s02` → [s03](../s03_staging_area/) → ... → s12
> *"你不需要记住 commit hash。你只需要学会在时间树上前后移动。"*
>
> **前提知识**: 做过至少 3 次 commit（s01 的内容）。知道 `git log` 和 `git commit`。

---

## 1. 为什么需要浏览历史？

做项目时，你会频繁遇到这些场景：

- 「上周五下午那个版本是正常的，现在坏了——我想看看当时的样子」
- 「这个 bug 是什么时候引入的？谁改的？」
- 「我想回到 3 个 commit 之前的状态，试试另一种方案」
- 「这行代码是谁写的？为什么这么写？」

Git 的答案：**你随时可以回到时间树上的任意节点，查看那个时刻的完整项目快照。**

---

## 2. 在时间树模型下理解

```
时间树:

    ●  a1b2c3d  "第一次提交"（根节点）
    │
    ●  b2c3d4e  "添加版本号"
    │
    ●  c3d4e5f  "添加作者信息"  ← main (HEAD)

HEAD = 「你现在站在哪个节点」

git checkout <某个节点> = 把 HEAD 移动到那个节点
  → 你的工作区会变成那个节点时的样子
  → 这就是「时间旅行」

git log = 从 HEAD 开始，沿着 parent 指针往回走，打印每个节点
```

---

## 3. git log — 查看时间线的各种方式

### 3.1 基础 log

```bash
git log
```
显示完整的提交历史：hash、作者、时间、信息。按时间倒序。

### 3.2 简洁模式

```bash
git log --oneline
```
每个 commit 一行：`a1b2c3d 提交信息`

### 3.3 显示改了什么

```bash
git log -p           # 显示每个 commit 的完整 diff
git log --stat       # 显示每个 commit 改了哪些文件（统计）
```

### 3.4 图形化显示分支

```bash
git log --graph --oneline --all --decorate
```

这就是我们「时间树」可视化的核心命令：
- `--graph`：画 ASCII 线条连接 commit
- `--oneline`：每个 commit 一行
- `--all`：显示所有分支（不只是当前分支）
- `--decorate`：显示分支名、HEAD、tag 标签

> **这是你以后最常用的 git log 命令。记不住就记一个缩写：**
> ```bash
> git log --graph --oneline --all
> ```

### 3.5 限制数量

```bash
git log -3            # 只看最近 3 个 commit
git log --since="2026-06-01"  # 只看 6 月以后的
git log --author="zhangsan"   # 只看某人的提交
```

---

## 4. git checkout / switch — 时间旅行

### 4.1 切换到某个 commit

```bash
git checkout <commit-hash>
```

**发生了什么？** Git 做了三件事：
1. 把 HEAD 移动到指定的 commit 节点
2. 把工作区的所有文件替换为该节点的快照内容
3. 进入「detached HEAD」状态（详见 5.2）

```bash
# 例子
git checkout a1b2c3d   # 回到"第一次提交"时的状态
# 看看那时候的文件...
git checkout main      # 回到最新的 main 分支
```

### 4.2 切换到某个分支

```bash
git checkout main       # 回到 main 分支的最新 commit
git switch main         # 新命令（Git 2.23+），和 checkout 一样但更清晰
```

> `git checkout` 身兼两职：切换分支 + 恢复文件。Git 2.23 引入 `git switch`（切换分支）和 `git restore`（恢复文件）来分离职责。本教程后面都用 `switch` 切换分支。

### 4.3 用相对引用

你不需要记住 hash！Git 支持相对引用：

```bash
git checkout HEAD~1    # 回到「上一个 commit」（HEAD 的 parent）
git checkout HEAD~2    # 回到「上上个 commit」
git checkout HEAD~3    # 回到 3 个 commit 之前
```

```
HEAD~1 = HEAD 的 parent
HEAD~2 = HEAD 的 parent 的 parent

    ●  HEAD~2  "第一次提交"
    │
    ●  HEAD~1  "添加版本号"
    │
    ●  HEAD    "添加作者信息"  ← 你现在在这
```

---

## 5. 关键概念深入

### 5.1 HEAD 是什么？（深入版）

`HEAD` 是一个存放在 `.git/HEAD` 里的文件。内容通常是：

```
ref: refs/heads/main
```

意思是「HEAD 指向 main 分支，main 分支指向某个 commit」。

```
HEAD → main → c3d4e5f（commit hash）

当你做新 commit 时:
  HEAD → main → 新 commit（main 自动更新）
```

### 5.2 Detached HEAD — 「游离状态」

当你 `git checkout <commit-hash>` 而不是分支名时：

```
HEAD → c3d4e5f（直接指向 commit，不通过分支）

此时做新 commit:
  HEAD → 新 commit → c3d4e5f
  但 main 还留在原地！
```

这就是 **detached HEAD**——HEAD 直接指向一个 commit，而不是通过分支名。

```
正常的 HEAD:
  HEAD → main → commit C

Detached HEAD:
  HEAD → commit B（没有分支名）
```

**Detached HEAD 下做的 commit 很危险**——如果你切换到其他分支，那些 commit 就找不到了（除非用 reflog，见 s11）。

> **什么时候需要 Detached HEAD？**
> - 只是想「看看」某个历史时刻的代码（不做改动）
> - 测试某个旧版本的行为
> - 从某个历史点开始做实验（但建议先建分支）

---

## 6. 常见错误（新手必读）

### ❌ 错误 1：`git checkout` 一个 hash，然后做了 commit，再切走——commit 丢了

```bash
git checkout a1b2c3d   # 进入 detached HEAD
# 改了代码...
git commit -m "实验"    # 新 commit 挂在 detached HEAD 下面
git checkout main       # ❌ 那个"实验" commit 找不到了！
```

> **修复**：用 `git reflog` 找回（见 s11）。或者在 checkout hash 之前先建分支：
> ```bash
> git switch -c experiment a1b2c3d  # 从 a1b2c3d 创建分支，安全！
> ```

### ❌ 错误 2：工作区有未提交的改动就 checkout

```bash
# 改了 README.md，但没 add 没 commit
git checkout main
# 可能报错: "error: Your local changes to the following files would be overwritten"
# 或强制覆盖你的改动！
```

> **规则**：切换分支前，要么提交改动，要么用 `git stash` 暂存（见 s10）。

---

## 7. 你学到了什么

| 概念 | 具体操作 |
|------|---------|
| `git log --oneline` | 简洁查看提交历史 |
| `git log --graph --all` | 可视化时间树（最常用的 log 命令） |
| `git log -p` | 查看每个 commit 具体改了什么 |
| `git log -3` | 限制查看数量 |
| `git checkout <hash>` | 时间旅行——回到任意历史节点 |
| `HEAD~1`, `HEAD~2` | 相对引用——不需要记 hash |
| Detached HEAD | HEAD 不指向分支，直接指向 commit |

---

## 8. 自己动手

1. **在你的学习仓库里**：做 5 个不同的 commit，每次改不同的文件
2. **用 `git log --graph --oneline --all`** 观察时间树
3. **用 `git checkout HEAD~2`** 回到 2 个 commit 之前——看看你的文件变回去了吗？
4. **用 `git log --stat`** 看每个 commit 改了哪些文件
5. **体验 detached HEAD**：`git checkout <最早那个commit的hash>`，然后 `git log` 看看有什么不同

---

> **下一章：[s03: 理解暂存区](../s03_staging_area/)** — 彻底搞懂 Git 最容易被误解的概念
