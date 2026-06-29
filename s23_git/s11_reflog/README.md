# s11: 时间旅行 — reflog：Git 的黑匣子

[s10](../s10_fine_operations/) → `s11` → [s12](../s12_internals/)
> *"在 Git 里，没有什么是真正丢失的。reflog 记录了你的每一步操作。"*
>
> **前提知识**: 用过 reset、rebase、branch 等操作（s04-s10）。

---

## 1. 为什么需要 reflog？

每个人都会犯错误：

- `git reset --hard` 之后发现删错了 commit
- `git branch -D` 之后发现那个分支还有用
- `git rebase` 之后发现搞砸了
- 「我刚才在哪个 commit 上来着？」

**reflog = Git 的「黑匣子」。** 它记录了 HEAD 和分支指针的**每一次移动**。

> reflog 是 Git 给你最大的安全感——你知道你可以撤销任何操作。

---

## 2. 在时间树模型下理解 reflog

```
reflog 记录的每一条 = HEAD 在时间树上的「移动轨迹」

时间树:
    ○  commit A  ← HEAD 1 小时前在这
    │
    ○  commit B  ← HEAD 30 分钟前在这
    │
    ○  commit C  ← HEAD 10 分钟前在这
    │
    ●  commit D  ← HEAD 现在在这（你刚做了 reset --hard）

git reflog:
    d4e5f6g HEAD@{0}: reset: moving to HEAD~1
    c3d4e5f HEAD@{1}: commit: 添加了重要功能   ← 这就是你想要恢复的！
    b2c3d4e HEAD@{2}: checkout: moving to main
    a1b2c3d HEAD@{3}: commit: 初始提交
```

> reflog 让你可以在时间树上「时间旅行」——回到之前 HEAD 指向过的任何节点。

---

## 3. reflog 核心命令

### 3.1 查看 reflog

```bash
git reflog                          # HEAD 的移动记录
git reflog show main                # main 分支的移动记录
git reflog --date=iso               # 带时间戳
```

### 3.2 用 reflog 恢复「丢失」的 commit

```bash
# 场景: 你 git reset --hard HEAD~3
# 然后发现那 3 个 commit 里有重要代码

git reflog                          # 找到 reset 之前的 HEAD 位置
# c3d4e5f HEAD@{1}: commit: 重要功能

git checkout c3d4e5f                # 跳到那个状态看看
# 或
git reset --hard c3d4e5f            # 直接回到那个状态
# 或
git branch recovered-branch c3d4e5f # 创建一个新分支指向那个 commit
```

### 3.3 用 reflog 恢复误删的分支

```bash
# 场景: git branch -D feature-important
# 那个分支的 commit 还在！

git reflog                          # 找到分支被删前指向的 commit
# 假设在 78a9b0c 这个 commit 时分支还存在

git branch feature-important 78a9b0c  # 复活！
```

### 3.4 用时间引用

```bash
git checkout HEAD@{1}               # 回到「上一次 HEAD 所在的位置」
git checkout HEAD@{10.minutes.ago}  # 回到 10 分钟前的状态
git checkout HEAD@{yesterday}       # 回到昨天的状态
```

---

## 4. reflog vs git log

| | git log | git reflog |
|------|---------|
| 记录什么 | 当前分支的 commit 历史 | HEAD 和分支的移动记录 |
| 能看到已删除的分支吗？ | ❌ 不能 | ✅ 能（只要时间不长） |
| 能看到 reset 前的 commit 吗？ | ❌ 不能 | ✅ 能 |
| 会过期吗？ | 不会（只要 commit 可达） | 会（默认 90 天清理不可达的） |

> **简单说**：`git log` 是时间树的历史。`git reflog` 是你操作的日记本。树可能被修剪，但日记不会骗你。

---

## 5. 常见救援场景

### 场景 1：reset --hard 搞错了

```bash
git reset --hard HEAD~5    # 删多了！

# 救援:
git reflog
# 找到 reset 之前的 HEAD 位置，比如 HEAD@{1}
git reset --hard HEAD@{1}  # 回到 reset 之前的状态
```

### 场景 2：误删未合并的分支

```bash
git branch -D feature-experiment   # 删了！

# 救援:
git reflog --date=iso
# 找到删分支时的 commit hash
git branch feature-experiment <hash>
```

### 场景 3：rebase 搞砸了

```bash
git rebase main           # 过程中出问题了
# 或 rebase 完了发现结果不对

# 救援:
git reflog
# 找到 rebase 之前的 HEAD@{N}
git reset --hard HEAD@{N}  # 回到 rebase 之前
```

---

## 6. reflog 的局限性

- **不是永久的**：Git 默认每 90 天清理一次不可达的 reflog 条目
- **不会共享**：reflog 是本地的——push 和 pull 不会同步 reflog
- **只记录 HEAD/分支移动**：不记录工作区的修改（工作区改动没 commit 就丢了，reflog 救不了）

---

## 7. 你学到了什么

| 概念 | 一句话 |
|------|--------|
| reflog | Git 的黑匣子——记录 HEAD 的每一步移动 |
| `git reflog` | 查看操作日志 |
| `HEAD@{1}` | 「上一步 HEAD 的位置」 |
| 恢复误删分支 | `git branch <name> <hash>` |
| 撤销错误的 reset/rebase | `git reset --hard HEAD@{N}` |
| 局限性 | 本地有效、会过期（90天）、不救未 commit 的改动 |

---

## 8. 自己动手

1. **故意做一次危险的 reset**：`git reset --hard HEAD~2`，然后用 `git reflog` 找回来
2. **创建一个分支，做几个 commit，然后删除分支**：用 reflog + `git branch` 恢复它
3. **用 `HEAD@{1}` 和 `HEAD@{10.minutes.ago}`** 体验时间引用
4. **对比 `git log` 和 `git reflog`**：reset 之后两个命令的输出有什么不同？
5. **做一个 rebase，然后用 reflog 回到 rebase 之前的状态**

---

> **下一章：[s12: 深入 .git](../s12_internals/)** — 打开 .git 目录，看清 Git 的内部原理
