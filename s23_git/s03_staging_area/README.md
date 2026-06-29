# s03: 理解暂存区 — Git 最容易被误解的概念

[s02](../s02_browsing_history/) → `s03` → [s04](../s04_branches/) → ... → s12
> *"暂存区不是多余的步骤。它让你选择性地构建下一个版本。"*
>
> **前提知识**: 做过多次 commit（s01），知道 git log 和 git checkout（s02）。

---

## 1. 为什么需要暂存区？

很多 Git 新手会问：「为什么不能像保存文件那样，一次操作就完成版本记录？为什么要先 add 再 commit？」

答案：**因为你一次可能改了 5 个文件，但其中只有 3 个属于「修复 bug」，另外 2 个属于「开发新功能」。暂存区让你能分开提交。**

```
场景: 你在修一个紧急 bug，同时也在做一个新功能

改动:
  fix_bug.py      ← 属于「修复登录 bug」
  test_fix.py     ← 属于「修复登录 bug」
  new_feature.py  ← 属于「新功能」（还在开发中）
  config.py       ← 属于「修复登录 bug」（改了配置）

没有暂存区 → 4 个文件全混在一个 commit 里
有暂存区   → 只 add 前 3 个文件，commit「修复登录 bug」
            → new_feature.py 留在工作区，继续开发
```

> **暂存区 = 你选择的「下一张快照要拍哪些文件」**

---

## 2. 在时间树模型下理解三个区域

```
工作区 (Working Directory)          暂存区 (Staging Area)        仓库 (Repository)
┌──────────────────┐               ┌──────────────┐           ┌──────────────────┐
│ 你的文件（真实存在） │  git add     │ 准备拍照的    │ git commit│ 时间树上的快照    │
│ fix_bug.py        │ ───────────→  │ fix_bug.py   │ ────────→ │ 历史 commit 节点  │
│ test_fix.py       │              │ test_fix.py  │           │                  │
│ new_feature.py    │              │ config.py    │           │                  │
│ config.py         │              │              │           │                  │
│                   │ git restore  │              │           │                  │
│                   │ ←─────────── │              │           │                  │
└──────────────────┘              └──────────────┘           └──────────────────┘

     git restore <file>              git restore --staged <file>
     (丢弃工作区改动)                (从暂存区撤出，回到工作区)
```

### 每一步发生了什么

```bash
# 1. 修改文件
vim fix_bug.py
# → 工作区变了，暂存区和仓库没变

# 2. git add
git add fix_bug.py
# → 工作区的内容被复制到暂存区
# → 现在暂存区和仓库不一样了（暂存区有新的 fix_bug.py）

# 3. git commit
git commit -m "修复登录 bug"
# → 暂存区的内容被拍成快照，生成新 commit 节点
# → 暂存区被清空
# → 现在三个区域又一致了（相对于最新 commit）
```

---

## 3. git status — 读懂它说的每一句话

`git status` 是 Git 里最有用的「诊断」命令。它告诉你三个区域之间的关系。

### 3.1 典型输出解读

```bash
$ git status

On branch main                           ← 你在哪个分支

Changes to be committed:                 ← 暂存区有东西（已 add，未 commit）
  (use "git restore --staged <file>..." to unstage)
        modified:   fix_bug.py

Changes not staged for commit:           ← 工作区有改动（改了但没 add）
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes)
        modified:   new_feature.py

Untracked files:                         ← 新文件，Git 从未跟踪过
  (use "git add <file>..." to include in what will be committed)
        new_script.py
```

### 3.2 三种文件状态

| 状态 | 含义 | 在哪里 |
|------|------|--------|
| **Changes to be committed** | 已 add，等着 commit | 暂存区 |
| **Changes not staged** | 改了，但没 add | 工作区（被 Git 跟踪的文件） |
| **Untracked** | 新文件，从未被 add 过 | 工作区（未被 Git 跟踪的文件） |

---

## 4. git diff — 看具体改了什么

### 4.1 三种比较

```bash
git diff                   # 工作区 vs 暂存区：改了但还没 add 的是什么？
git diff --staged          # 暂存区 vs 最新 commit：下次会提交什么？
git diff HEAD              # 工作区 vs 最新 commit：所有未提交的改动
```

```
                    git diff                       git diff --staged
    工作区  ←──────────────→  暂存区  ←──────────────────→  仓库 (HEAD)
            工作区 vs 暂存区          暂存区 vs 最新 commit

               git diff HEAD
    工作区  ←─────────────────────────────────────────────→  仓库 (HEAD)
                         所有未提交的改动
```

### 4.2 读 diff 输出

```diff
diff --git a/fix_bug.py b/fix_bug.py
index a1b2c3d..e4f5g6h 100644
--- a/fix_bug.py         ← 旧文件
+++ b/fix_bug.py         ← 新文件
@@ -10,6 +10,8 @@        ← 从旧文件的第 10 行开始，显示了 6 行；在新文件里是 8 行
 def login(user):
-    if user.password:   ← 删掉的行（-）
+    if user.password and user.is_active:  ← 加上的行（+）
+        log_login(user)  ← 加上的行（+）
     return True
```

- `-` 开头 = 旧版本有，新版本删了
- `+` 开头 = 新版本有，旧版本没有
- `@@ -10,6 +10,8 @@` = 位置信息（从第 10 行开始）

---

## 5. git restore — 撤回改动

### 5.1 从暂存区撤回（unstage）

```bash
git restore --staged fix_bug.py
# 把 fix_bug.py 从暂存区「撤出」→ 回到工作区
# 相当于 git add 的反操作
# 文件内容不变，只是不再在「下次提交」的队列里了
```

### 5.2 丢弃工作区改动

```bash
git restore fix_bug.py
# ⚠️ 危险操作！工作区的改动会被丢弃，恢复到当前 commit 的版本
# 使用前确认你不需要这些改动
```

---

## 6. 为什么暂存区是天才设计？

回顾一下，暂存区让你能做这些事：

1. **选择性提交**：改了 5 个文件，只提交其中 3 个
2. **拆分大改动**：一个大功能可以拆成多个逻辑清晰的 commit
3. **预览**：`git diff --staged` 让你在提交前最后确认一遍
4. **精细控制**：一个文件里改了 10 行，可以只 add 其中 5 行（`git add -p`）

> **没有暂存区的工具**：要么全提交，要么全不提交。Git 给了你更多控制。

---

## 7. 常见错误（新手必读）

### ❌ 错误 1：改了文件忘了 add 就 commit

```bash
# 改了 README.md
git commit -m "更新文档"   # ❌ 什么都没提交！
# Git: "nothing to commit, working tree clean"
# 原因: 改了文件但没 add，暂存区是空的
```

### ❌ 错误 2：add 完又改了文件才 commit

```bash
git add README.md           # 暂存区 = 版本 A
# 又改了 README.md          # 工作区 = 版本 B（版本 A + 新的改动）
git commit -m "更新文档"    # 提交的是版本 A，版本 B 的新改动没有进入 commit！
```

> **解决**：commit 之前再 `git add` 一次，或者 `git diff` 确认暂存区和工作区一致。

### ❌ 错误 3：混淆 `git restore` 和 `git restore --staged`

```bash
git restore --staged file   # ✅ 只是从暂存区撤出，工作区的改动保留
git restore file            # ⚠️ 丢弃工作区改动！恢复成当前 commit 的版本
```

---

## 8. 你学到了什么

| 概念 | 具体操作 |
|------|---------|
| 三个区域 | 工作区（编辑）→ 暂存区（add）→ 仓库（commit） |
| `git status` | 诊断三个区域之间的关系 |
| `git diff` | 工作区 vs 暂存区 |
| `git diff --staged` | 暂存区 vs 最新 commit（下次会提交什么） |
| `git restore --staged <file>` | 从暂存区撤出（unstage） |
| `git restore <file>` | 丢弃工作区改动（危险操作） |
| 暂存区的价值 | 选择性提交、拆分 commit、提交前预览 |

---

## 9. 自己动手

1. **在你的学习仓库里**：同时改 3 个文件，只 add 其中 2 个，commit，观察剩下的文件怎么了
2. **用 `git status`** 在每一步（改文件后、add 后、commit 后）都运行一次，读它的输出
3. **用 `git diff` 和 `git diff --staged`** 对比，理解两种比较的区别
4. **add 完后继续改同一个文件**，然后用 `git status` 看——文件同时出现在 "staged" 和 "not staged" 里
5. **用 `git restore --staged`** 把一个文件从暂存区撤回

---

> **下一章：[s04: 分支](../s04_branches/)** — 创建时间线的平行宇宙
