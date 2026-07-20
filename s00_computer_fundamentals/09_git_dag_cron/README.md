# s00-09: Git、DAG、Cron

[← 返回概览](../README.md) | [上一章：HTTP/网络](../08_http_network/)

> *Git 管理代码版本，DAG 表达任务依赖，Cron 定时触发任务。这三个是 Agent 工程中必须认识的"基础设施工具"。*

---

## 问题 — Agent 怎么管理代码、任务、时间？

- **Git**：s18 的工作树隔离依赖 `git worktree`——不理解 Git 就不理解 s18
- **DAG**：s12 的任务系统用 DAG 表达"先做完 A 才能做 B"——不理解 DAG 就不理解任务依赖
- **Cron**：s14 的定时调度用 Cron 表达式决定什么时候触发——不理解 Cron 就不理解定时任务

---

## 核心概念

### 1. Git — 代码的"时光机"

```
commit = 一次保存的快照（SHA-1 hash 标识）
branch = 一条独立的开发线（指向某个 commit 的指针）
worktree = 同一仓库的多份工作副本，每份在不同目录
```

**s18 本质就是 `git worktree add`**：

```bash
git worktree add /tmp/isolated-work feature-branch
# → 在 /tmp/isolated-work 创建一个独立的工作副本
# → 可以随便改，不影响主工作区
# → 用完了 git worktree remove 删掉
```

### 2. DAG — 有向无环图

```
A ──→ B ──→ D
  └─→ C ──┘
```

- **有向**：依赖有方向（B 依赖 A，不是反过来）
- **无环**：不能绕回来（A→B→C→A 不合法）

s12 的 Task 系统：

```json
{
  "id": "task-4",
  "title": "部署到生产",
  "blockedBy": ["task-2", "task-3"]
}
```

Task-4 只有在 task-2 和 task-3 都完成后才能开始。**拓扑排序**找出可行的执行顺序。

### 3. Cron — 定时任务

```
┌─ 分 (0-59)
│ ┌─ 时 (0-23)
│ │ ┌─ 日 (1-31)
│ │ │ ┌─ 月 (1-12)
│ │ │ │ ┌─ 星期 (0-6, 0=周日)
│ │ │ │ │
* * * * *
```

常用例子：
- `0 9 * * 1` — 每周一早上 9 点
- `*/5 * * * *` — 每 5 分钟
- `0 0 1 * *` — 每月 1 号零点

---

## 跟 Agent 的关系

| 章节 | 工具 |
|------|------|
| **s05** | TodoWrite 列表 = DAG 的简化版 |
| **s12** | Task 系统 = 完整的 DAG + 拓扑排序 |
| **s14** | Cron 调度器用 Cron 表达式触发任务 |
| **s18** | 工作树隔离 = `git worktree add` |

---

## 试一下

```bash
python 09_git_dag_cron/code.py
```

---

## 小结

```
Git: commit = 快照, branch = 工作线, worktree = 独立副本
DAG: 有向无环图, 拓扑排序, 表达任务依赖
Cron: 5 字段表达式, 定时触发, s14 的核心
```
