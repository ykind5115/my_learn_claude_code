# s10: 精细操作 — stash、cherry-pick、reset

[s09](../s09_rebase/) → `s10` → [s11](../s11_reflog/) → s12
> *"这些命令不是魔法。它们都是在时间树上移动指针——只是移动的方式不同。"*
>
> **前提知识**: 理解 commit、branch、HEAD（s01/s02/s04）。

---

## 1. 为什么需要这些「杂项」命令？

日常开发中，你会遇到这些场景：

- 「改了一半，突然要切分支修 bug——但不想 commit 半成品」
- 「别的分支上有个 commit 写得很好，我想直接拿过来用」
- 「刚才的 commit 有问题，我想撤回但保留改动」

`stash`、`cherry-pick`、`reset` 就是为这些场景设计的。它们都可以用时间树模型统一理解。

---

## 2. git stash — 暂时把改动收起来

### 场景

```
你正在 feature 分支上改代码，还没改完：
  工作区有一堆改动，暂存区也有东西

突然老板说：线上出 bug 了，马上修！

你不能 commit 半成品（不规范的 commit）
你也不能直接 switch 到 main（工作区有未保存的改动）
```

### stash 在时间树上的理解

```
git stash = 把工作区和暂存区的改动「暂存」到一个临时区域
           → 工作区变干净
           → 你可以自由切换分支
           → 回来时用 git stash pop 恢复
```

### 核心命令

```bash
git stash                    # 暂存所有改动
git stash save "描述"        # 暂存 + 加描述
git stash list               # 查看所有 stash
git stash pop                # 恢复最近的 stash 并删除
git stash apply              # 恢复但不删除
git stash drop               # 删除一个 stash
```

---

## 3. git cherry-pick — 从别的分支「摘」一个 commit

### 场景

```
你发现 feature-search 分支上有个 commit 写了一个很好的工具函数。
你想把这个 commit 拿到你当前的 feature-login 分支上用。
但你不想把整个 feature-search 合并过来。
```

### cherry-pick 在时间树上的理解

```
cherry-pick = 把某个 commit 的「改动内容」复制一份，作为一个新 commit 挂到当前分支

    main:  A──B──C──D  ← 当前 HEAD
         /
  other: E──F──G
            ↑
        想摘 F 这个 commit

    git cherry-pick F

    main:  A──B──C──D──F'  ← F 的内容，新的 commit hash
         /
  other: E──F──G
```

### 命令

```bash
git cherry-pick <commit-hash>            # 摘一个 commit
git cherry-pick <hash1>..<hash2>         # 摘一个范围的 commit（不包含 hash1）
```

---

## 4. git reset — 移动分支指针

### reset 在时间树上的理解

```
reset 就是「把当前分支的标签移到另一个节点上」。

    HEAD → main → commit D
    ○──○──○──●  ← main
       ↑
     移到这

    git reset <commit B 的 hash>

    HEAD → main → commit B
    ○──○──○──●  ← 节点 C 和 D 还在，但 main 不指向它们了
       ↑
     现在 main 在这
```

### 三种 reset 模式

| 模式 | 分支指针 | 暂存区 | 工作区 | 用途 |
|------|---------|--------|--------|------|
| `--soft` | 移动 | 不变 | 不变 | 「commit 错了，想重新 commit」 |
| `--mixed`（默认） | 移动 | 重置 | 不变 | 「add 和 commit 都想撤回」 |
| `--hard` | 移动 | 重置 | 重置 | 「全部丢弃，回到某个状态」⚠️ |

```bash
git reset --soft HEAD~1    # 撤销上次 commit，改动留在暂存区
git reset HEAD~1           # 撤销上次 commit 和 add，改动留在工作区
git reset --hard HEAD~1    # ⚠️ 撤销一切，回到上一个 commit 的状态
```

### 图解

```
原始状态:
  工作区: clean    暂存区: clean    仓库: ○─○─● main (HEAD)

git reset --soft HEAD~1:
  工作区: clean    暂存区: 有内容   仓库: ○─● main (HEAD)
  用途: "commit 信息写错了，改完重新 commit"

git reset (--mixed) HEAD~1:
  工作区: 有内容   暂存区: clean    仓库: ○─● main (HEAD)
  用途: "连 add 都要撤回，从头开始"

git reset --hard HEAD~1:
  工作区: clean    暂存区: clean    仓库: ○─● main (HEAD)
  用途: "全不要了，回到上一个干净的状态" ⚠️ 危险！
```

---

## 5. 常见错误（新手必读）

### ❌ 错误 1：`git reset --hard` 后后悔了

```bash
git reset --hard HEAD~3   # 删掉了 3 个 commit 的内容
# "等等，我里面有重要的代码！"
```

> **修复**：`git reflog` 找回（见 s11）。reset --hard 不是真的删除，commit 还在 .git 里。

### ❌ 错误 2：stash 太多忘了清理

```bash
git stash list
# stash@{0}: ...
# stash@{1}: ...
# stash@{2}: ...
# stash@{3}: ...  ← 三个月前的，早忘了是什么
```

> **建议**：用完就 `git stash pop`，不要攒 stash。

### ❌ 错误 3：cherry-pick 了不该 pick 的 commit

> cherry-pick 产生的新 commit 和原 commit 没有关联——Git 不知道它们是「同一个改动」。后续合并可能会有重复冲突。

---

## 6. 你学到了什么

| 命令 | 时间树模型理解 | 用途 |
|------|---------------|------|
| `git stash` | 把改动存到临时区域 | 切换分支前暂存半成品 |
| `git stash pop` | 恢复临时区域的改动 | 回来继续工作 |
| `git cherry-pick <hash>` | 复制一个节点到当前分支 | 从别的分支「借用」一个 commit |
| `git reset --soft HEAD~1` | 撤销 commit，保留 add | 重新写提交信息 |
| `git reset HEAD~1` | 撤销 commit 和 add | 从头修改 |
| `git reset --hard HEAD~1` | 完全回到上一个节点 | 放弃一切改动 |

---

## 7. 自己动手

1. **stash 练习**：在分支上改文件，不 commit，`git stash`，切到 main，再切回来，`git stash pop`
2. **cherry-pick 练习**：创建两个分支，在 A 上做 commit，切到 B，`git cherry-pick` 把 A 的 commit 摘过来
3. **reset --soft 练习**：做一个 commit，然后用 `git reset --soft HEAD~1`——看 commit 被撤销了但改动回到了暂存区
4. **reset --hard 小范围练习**：做一个 commit（内容不重要），`git reset --hard HEAD~1`——然后马上用 `git reflog` 看能不能找回来（预热 s11）

---

> **下一章：[s11: 时间旅行](../s11_reflog/)** — reflog：Git 的黑匣子，撤销一切操作
