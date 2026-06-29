# s08: 协作工作流 — 团队开发的标准化流程

[s07](../s07_remote/) → `s08` → [s09](../s09_rebase/) → ... → s12
> *"Git 给了你操作时间树的能力。工作流告诉你「在团队里应该怎么用」。"*
>
> **前提知识**: 理解 push/pull/fetch（s07），理解分支和合并（s04-s06）。

---

## 1. 为什么需要工作流？

Git 本身不强制任何规则——你可以直接在 main 上 commit，可以 force push，可以做任何事。

**但团队需要规则**。不然就会：

- 张三直接 push 到 main，李四的代码被覆盖
- 5 个人同时改 main，冲突每天 10 次
- 没人知道哪个版本是「可以发布的」
- 代码没有经过 review 就上线，bug 层出不穷

> **工作流 = 团队约定的协作规则。Git 提供机制，工作流提供策略。**

---

## 2. GitHub Flow — 最流行的工作流

GitHub Flow 是最简单、最常用的协作工作流。它只有 6 个步骤：

```
 1. 从 main 创建 feature 分支
    git switch -c feature-xxx

 2. 在 feature 分支上开发和 commit
    git add ... → git commit → 重复...

 3. 定期 push 到远程（备份 + 共享）
    git push -u origin feature-xxx

 4. 在 GitHub 上创建 Pull Request
    "请把我的 feature-xxx 合并到 main"

 5. 队友 Code Review
    讨论、修改、push 新 commit

 6. 合并到 main + 删除 feature 分支
    通过 PR 页面点 "Merge"
```

### 时间树视角

```
初始:
    main:  ○───○───○

创建分支并开发:
    main:  ○───○───○
                    \
    feature:          ○───○───●

创建 PR → Review → Merge:
    main:  ○───○───○───○───○───● (merge commit)
                    \         /
    feature:          ○───○───●
                              ↑
                          分支被删除
```

---

## 3. Pull Request 是什么？

Pull Request（PR）不是 Git 的命令——它是 GitHub/GitLab 的功能。

**PR = 「我改好了，请帮我合并到 main」的请求。**

一个 PR 包含：
1. 源分支（feature-xxx）和目标分支（main）
2. 所有 commit 的差异总览
3. 讨论区——队友可以逐行评论
4. CI/CD 状态——自动测试是否通过

> **PR 的核心价值**：在代码进入 main 之前，让另一个人看过、讨论过、确认过。

---

## 4. Code Review 的基本原则

| 原则 | 说明 |
|------|------|
| **Review 代码，不是 Review 人** | "这行代码可以改成 xxx" 而非 "你怎么这么写" |
| **每次 PR 要小** | 200 行以内的 PR review 效果最好 |
| **一个 PR = 一个逻辑改动** | 不要把一个 PR 里塞 3 个无关的功能 |
| **Review 是双向学习** | 写的人学到更好的写法，Review 的人了解新代码 |

---

## 5. 冲突在工作流中怎么处理？

```
场景: 张三的 PR #1 先合并了（改了 app.py）
      李四的 PR #2 也改了 app.py——现在有冲突

解决方案:
  1. 李四在本地执行:
     git switch main
     git pull                    # 拉取张三的合并
     git switch feature-lisi
     git merge main              # 把最新的 main 合并到自己的分支
     # 解决冲突...
     git push                    # push 解决后的版本
  2. PR 页面上的冲突标记消失，可以合并了
```

> **规则**：谁后合并，谁负责解决冲突。先合并的人不用管。

---

## 6. 日常开发的一天

```
早上:
  git switch main
  git pull                        # 拉取昨晚队友的更新
  git switch -c feature-today     # 创建今天的分支

开发中（每个小功能完成就 commit）:
  git add src/xxx.py
  git commit -m "完成用户列表查询功能"
  git push -u origin feature-today  # 备份到远程

准备下班:
  # 如果功能做完了 → 去 GitHub 开 PR
  # 如果没做完 → push 到远程，明天继续
  git push
```

---

## 7. 你学到了什么

| 概念 | 一句话 |
|------|--------|
| GitHub Flow | 6 步标准协作流程 |
| Pull Request | 请求把你的分支合并到 main |
| Code Review | 代码进入 main 之前的质量关卡 |
| 冲突处理 | 后合并的人负责 rebase/merge main |
| 小 PR | 越小越好 review，越快合并 |

---

## 8. 自己动手

1. **在 GitHub 上**：fork 一个开源项目，clone 到本地，创建分支，改点东西，push，开一个 PR
2. **模拟 Review**：找一个朋友，互相 review 对方的代码（哪怕是模拟的）
3. **体验完整流程**：main → branch → commit → push → PR → review → merge → delete branch
4. **故意制造 PR 冲突**：两个分支改同一个文件，看 GitHub 的冲突提示

---

> **下一章：[s09: rebase](../s09_rebase/)** — 改写历史，让时间线更干净
