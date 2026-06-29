# s09: rebase — 把树枝「嫁接」到别处

[s08](../s08_collaboration/) → `s09` → [s10](../s10_fine_operations/) → ... → s12
> *"merge 保留历史的真实形状。rebase 把历史整理成一条直线。各有各的用武之地。"*
>
> **前提知识**: 理解 merge（s05），理解分支（s04），用过远程仓库（s07）。

---

## 1. 为什么需要 rebase？

假设你在 feature 分支上开发了 3 天。这期间 main 前进了 5 个 commit。

**如果用 merge**：
```
main:    ○──○──○──○──○──● (merge commit)
          \             /
feature:   ○──○──○─────┘

结果: 时间树保留了真实的分叉形状。
```

**如果用 rebase**：
```
rebase 前:
main:    ○──○──○──○──○
          \
feature:   ○──○──○

rebase 后:
main:    ○──○──○──○──○──○──○──○
                          \
feature:                   (这 3 个 commit 的内容被「嫁接」过来了)

结果: 时间线是一条直线。feature 的 3 个 commit 看起来像是「在最新的 main 上开发的」。
```

> **merge = 保留历史真相。rebase = 整理历史外观。**
>
> 选择 merge 还是 rebase，取决于你想让时间树看起来像什么。

---

## 2. 在时间树模型下理解 rebase

### rebase 的本质

```
原始:
    main:  A──B──C──D
            \
    feature: E──F──G

git switch feature
git rebase main

过程:
    1. Git 找到共同祖先 B
    2. 把 E、F、G 三个 commit 的改动「暂存」起来
    3. 把 feature 的底座从 B 搬到 D（main 的最新节点）
    4. 把 E、F、G 的改动逐个应用到 D 上面
    5. 生成新的 E'、F'、G'（hash 变了）

结果:
    main:  A──B──C──D
                      \
    feature:            E'──F'──G'

原来的 E、F、G 还在 .git 里（reflog 能找到），但 feature 标签指向了新的 E'、F'、G'。
```

### rebase 和 merge 的对比

| | merge | rebase |
|------|--------|
| 产生新 commit？ | 产生一个 merge commit | 不产生 merge commit，但重新生成所有 feature commit |
| 历史形状 | 保留分叉结构 | 线性历史 |
| commit hash | 原来的不变 | feature 的所有 commit 重新生成（新 hash） |
| 能看到「什么时候从哪分出来的」？ | ✅ 能看到 | ❌ 被抹平了 |
| 适合场景 | 公共分支、长期分支 | 个人分支、整理未 push 的 commit |

---

## 3. 交互式 rebase — 整理 commit 历史

在合并到 main 之前，你可能有 10 个凌乱的 commit：

```
WIP: 还在写...
修了个 bug
WIP: 继续写
改了个变量名
终于完成了！
```

这些 commit 对 reviewer 不友好。交互式 rebase 让你在 push 之前整理它们。

```bash
git rebase -i HEAD~5     # 整理最近 5 个 commit
```

会打开编辑器：

```
pick a1b2c3d 添加登录功能
pick b2c3d4e WIP: 还在写...
pick c3d4e5f 修了个小 bug
pick d4e5f6g WIP: 继续写
pick e5f6g7h 登录功能完成
```

你可以改成：

```
pick a1b2c3d 添加登录功能
squash b2c3d4e WIP: 还在写...        # squash = 合并到上一个 commit
fixup c3d4e5f 修了个小 bug            # fixup = 合并 + 丢弃提交信息
squash d4e5f6g WIP: 继续写
reword e5f6g7h 登录功能完成            # reword = 修改提交信息
```

结果：5 个凌乱的 commit → 1 个干净的 commit：「实现用户登录功能」

### 交互式 rebase 命令一览

| 命令 | 作用 |
|------|------|
| `pick` | 保留这个 commit（默认） |
| `reword` | 保留但修改提交信息 |
| `squash` | 合并到上一个 commit，保留提交信息 |
| `fixup` | 合并到上一个 commit，丢弃提交信息 |
| `drop` | 删除这个 commit |
| `edit` | 停下来让你修改这个 commit 的内容 |

---

## 4. ⚠️ rebase 的黄金法则

> **不要 rebase 已经 push 到公共仓库的分支！**

为什么？

```
如果张三 rebase 了 feature-shared 分支并 push:
  远程:  E'──F'──G'（新的，hash 变了）
  李四本地:  E──F──G（旧的）

李四 pull 时:
  Git 发现同一个分支上出现了「两条不同的历史」
  → 李四需要手动处理，可能丢失工作
```

> **安全用法**：只 rebase 你**自己的**、**还没 push 的**、或者**只有你一个人用的**分支。

---

## 5. 什么时候用 merge，什么时候用 rebase？

| 场景 | 推荐 |
|------|------|
| 把 feature 合入 main | **merge**（保留痕迹） |
| 把 main 的更新同步到 feature | **rebase**（保持线性） |
| 整理自己还没 push 的 commit | `rebase -i` |
| 公共分支之间 | **merge**（绝不 rebase） |
| Pull 远程更新 | `git pull --rebase`（避免多余的 merge commit） |

---

## 6. 常见错误（新手必读）

### ❌ 错误 1：rebase 公共分支

```bash
git switch main
git rebase feature-xxx   # ❌ 不要 rebase main！
git push --force         # ❌ 更不要 force push！
# 队友们的本地 main 全都乱了
```

### ❌ 错误 2：rebase 中遇到冲突就慌了

```bash
git rebase main
# CONFLICT!
```

> rebase 中的冲突和 merge 中的冲突一样处理：**解决 → git add → git rebase --continue**。
> 不想继续了？`git rebase --abort` 回到 rebase 前。

---

## 7. 你学到了什么

| 概念 | 一句话 |
|------|--------|
| rebase | 把分支的「底座」搬到另一个 commit 上 |
| merge vs rebase | merge 保留分叉，rebase 产生线性历史 |
| `git rebase -i` | 交互式整理 commit（squash/fixup/reword/drop） |
| 黄金法则 | 不要 rebase 已 push 的公共分支 |
| `git pull --rebase` | pull 时用 rebase 代替 merge |

---

## 8. 自己动手

1. **创建一个 feature 分支**，做 3 个 commit。在 main 上也做 2 个 commit。然后用 `git rebase main`——看时间树变直了
2. **用 `git rebase -i HEAD~5`** 练习 squash 和 reword
3. **在 rebase 中故意让冲突发生**，练习 `git rebase --continue` 和 `git rebase --abort`
4. **对比 `git merge` 和 `git rebase`** 之后的时间树——哪种历史更清晰？

---

> **下一章：[s10: 精细操作](../s10_fine_operations/)** — stash、cherry-pick、reset：树的微操技巧
