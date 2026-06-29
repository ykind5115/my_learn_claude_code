# s05: 合并 — 两条时间线汇合

[s04](../s04_branches/) → `s05` → [s06](../s06_conflicts/) → ... → s12
> *"合并不是魔法。它只是找到两条线的共同祖先，然后告诉你差异在哪里。"*
>
> **前提知识**: 会创建和切换分支（s04），理解 commit 有 parent 指针（s01）。

---

## 1. 为什么需要合并？

分支让你平行开发，但最终你要把成果汇合到一起。

```
场景: feature-login 分支开发了 3 天，功能做完了。
现在需要把这个功能「合入」main 分支，让它成为正式版本的一部分。

    main:  ○───○───○
                \
    feature:      ○───○───○  ← 这 3 个 commit 需要合入 main
```

合并（merge）就是**把两条时间线上的改动，合成一个新的状态**。

---

## 2. 在时间树模型下理解合并

### 合并的本质

Git 合并做三件事：
1. 找到两个分支的**共同祖先**（分叉点）
2. 计算从共同祖先以来，两个分支各自改了什么
3. 把两边的改动合成一个结果

### 两种合并方式

#### Fast-forward merge（快进合并）

当一条分支完全在另一条分支的「前方」时：

```
合并前:
    main:  ○───○
                \
    feature:      ○───●  ← feature 在 main 的前方

合并后:
    main:  ○───○───○───●  ← main 直接"快进"到 feature 的位置
```

> 没有新 commit 产生。只是把 main 标签移到了 feature 的位置。

#### Three-way merge（三方合并）

当两条分支各自有了新 commit：

```
合并前:
    main:  ○───○───○───●
                \
    feature:      ○───●  ← 两条线都前进了

合并后:
    main:  ○───○───○───●───●  ← 新的 merge commit
                \         /
    feature:      ○───●───┘
                    ↑
              这个节点有两个 parent！
```

> 产生一个新的 **merge commit**。这个 commit 有两个 parent：一个来自 main，一个来自 feature。这就是时间树上「两条线汇合」的样子。

---

## 3. 怎么做 — 逐行讲解

### 3.1 Fast-forward merge

```bash
# 假设 feature 分支比 main 多 2 个 commit
git switch main
git merge feature-login

# 输出:
# Updating a1b2c3d..e4f5g6h
# Fast-forward
#  file.py | 5 +++++
#  1 file changed, 5 insertions(+)
```

**发生了什么？**
- Git 发现 feature-login 完全在 main 的前方（main 没有自己独有的 commit）
- 直接把 main 标签移动到 feature-login 的位置
- 没有创建新 commit

### 3.2 Three-way merge

```bash
# main 和 feature 各自都有了新 commit
git switch main
git merge feature-login

# Git 会打开编辑器让你写 merge commit 的信息
# 默认信息: "Merge branch 'feature-login' into main"
```

**发生了什么？**
- Git 找到共同祖先
- 计算两边的差异
- 如果没冲突，自动合成，创建一个 merge commit
- merge commit 有两个 parent

### 3.3 查看合并历史

```bash
git log --graph --oneline --all
# 你会看到两条线在 merge commit 处汇合
```

```
*   a1b2c3d Merge branch 'feature-login' into main   ← merge commit
|\
| * e4f5g6h 完成登录页面                               ← feature 的 commit
| * d3e4f5g 添加登录功能
* | c2d3e4f main 上的其他改动                          ← main 的 commit
|/
* b1c2d3e 共同祖先
```

---

## 4. 合并后删除分支

```bash
git branch -d feature-login    # 安全删除（已合并的）
```

删除后，时间树上的节点还在——只是「feature-login」这个标签没了。你可以通过 merge commit 找到这些节点。

---

## 5. 常见错误（新手必读）

### ❌ 错误 1：在错误的分支上执行 merge

```bash
git switch feature-login
git merge main        # ❌ 把 main 合并到 feature！
# 你想做的是把 feature 合入 main
```

> **规则**：先切换到「要合入的目标分支」，再 merge 源分支。
> ```bash
> git switch main           # 切换到目标分支
> git merge feature-login   # 把 feature 合入 main
> ```

### ❌ 错误 2：合并前不更新 main

```bash
git switch feature-login
# 开发了 3 天...
git switch main
git merge feature-login     # 没先 git pull！
# main 可能已经落后于远程仓库
```

> **正确做法**：合并前先 `git pull` 确保 main 是最新的。

### ❌ 错误 3：在 main 上有未提交的改动时就 merge

```bash
# 在 main 上改了文件，没 commit
git merge feature-login
# error: Your local changes would be overwritten by merge.
```

> **解决**：先 commit 或 stash，再 merge。

---

## 6. 你学到了什么

| 概念 | 一句话 |
|------|--------|
| Fast-forward merge | 一条线在另一条线前方 → 直接移动标签，不产生新 commit |
| Three-way merge | 两条线各自有新的 commit → 创建 merge commit（有两个 parent） |
| Merge commit | 特殊的 commit，有两个 parent，标记汇合点 |
| `git merge <branch>` | 把指定分支合并到当前分支 |
| 合并后删除分支 | 安全操作，节点和提交历史都保留 |

---

## 7. 自己动手

1. **创建两个分支**，各自做 2-3 个 commit，然后用 three-way merge 合并
2. **创建一个分支**，做 2 个 commit，然后用 fast-forward merge（main 不额外 commit）
3. **用 `git log --graph --all --oneline`** 看两种 merge 的时间树有什么不同
4. **合并后删掉 feature 分支**，看 `git log --graph` 确认节点还在
5. **在 main 上有未提交的改动时尝试 merge**，看 Git 的报错信息

---

> **下一章：[s06: 合并冲突](../s06_conflicts/)** — 当 Git 不知道选哪边时，你来做决定
