# s12: 深入 .git — Git 的内部原理

[s11](../s11_reflog/) → `s12`
> *"你看不到的东西也在掌控之中。打开 .git 看看，Git 的魔法不过是几个文件。"*
>
> **前提知识**: 用过 Git 的基本操作（s01~s11）。这一章不是必需的，但能让你从「会用」进阶到「理解」。

---

## 1. 为什么需要了解 .git 内部？

到这一章为止，你已经学会了 Git 的所有日常操作。但你可能还有这些问题：

- 「commit hash 那一长串乱码（`a1b2c3d...`）是什么？」
- 「为什么 Git 这么快？切换分支为什么是瞬间的？」
- 「Git 怎么保证数据不被篡改？」
- 「`.git/` 目录那么大，里面到底有什么？」

**这一章帮你打开黑箱**。不需要记细节——只需要理解 Git 的数据模型，所有操作都会变得更清晰。

---

## 2. .git 目录结构

```
.git/
├── HEAD              ← 「你现在在哪」——指向当前分支
├── config            ← 仓库级配置（user.name、remote 等）
├── description       ← 仓库描述（GitWeb 用）
│
├── objects/          ← ★ 核心！所有数据都存在这里
│   ├── info/
│   └── pack/         ← 打包后的对象（节省空间）
│
├── refs/             ← ★ 分支和标签指针
│   ├── heads/        ← 本地分支（每个文件 = 一个分支名）
│   │   ├── main      ← 内容是 "a1b2c3d..."
│   │   └── feature   ← 内容是 "e4f5g6h..."
│   ├── tags/         ← 标签
│   └── remotes/      ← 远程分支镜像
│       └── origin/
│           └── main  ← 内容是 "a1b2c3d..."
│
├── logs/             ← reflog 数据
├── hooks/            ← 钩子脚本（自动化触发）
├── index             ← ★ 暂存区（二进制文件）
└── info/
    └── exclude       ← 本地 ignore 规则（类似 .gitignore）
```

---

## 3. Git 对象模型：四种对象

Git 是一个**内容寻址的文件系统**。核心是四种对象：

```
blob ──→ tree ──→ commit ──→ ref（分支/标签）
(文件)   (目录)   (快照)     (人类可读的名字)
```

### 3.1 blob — 文件的内容

```
当你 git add 一个文件时，Git:
  1. 读取文件内容
  2. 计算 "blob <长度>\0<文件内容>" 的 SHA-1 哈希
  3. 以哈希为文件名，存入 .git/objects/
```

- blob 只存**内容**，不存文件名、权限等元信息
- 两个内容相同的文件 → 同一个 blob（节省空间！）

### 3.2 tree — 目录的快照

```
tree 对象记录了:
  - 目录里有哪些文件和子目录
  - 每个文件对应哪个 blob（通过 hash 引用）
  - 文件权限
```

tree 之于目录 = blob 之于文件。

### 3.3 commit — 时间树的一个节点

```
commit 对象包含:
  - 一个 tree 的引用（项目根目录的快照）
  - parent(s) — 父 commit 的引用（可能有多个 parent = merge commit）
  - author / committer / 时间戳
  - 提交信息
```

### 3.4 ref — 人类可读的标签

```
ref 就是 .git/refs/heads/main 这个文件，里面写了一行:
  a1b2c3d4e5f6789...（某个 commit 的 hash）

分支 = ref = 指向 commit 的指针。
```

---

## 4. 动手：偷看 Git 对象

```bash
# 查看某个对象的内容
git cat-file -p <hash>

# 查看某个对象是什么类型
git cat-file -t <hash>

# 例子:
git log --oneline                    # 拿一个 commit hash
git cat-file -p a1b2c3d              # 看 commit 对象的内容
# 输出:
# tree e4f5g6h...                   ← 这个 commit 指向的 tree
# parent 789abc...                  ← 父 commit
# author zhangsan <...>
# committer zhangsan <...>
# 提交信息

git cat-file -p e4f5g6h              # 再看 tree 对象
# 输出:
# 100644 blob a1b2c3d...   README.md
# 100644 blob d4e5f6g...   app.py
# 040000 tree f1g2h3i...   src/

git cat-file -p a1b2c3d              # 再看 blob 对象
# 输出: README.md 的文件内容
```

---

## 5. 为什么 Git 这么快？

| 设计 | 效果 |
|------|------|
| **内容寻址** | 相同内容 = 相同 hash = 只存一份 |
| **快照，不是差异** | checkout 不用计算差异，直接取出完整文件 |
| **压缩存储** | 定期把松散对象打包成 packfile |
| **本地操作** | commit/log/diff 都不需要网络 |
| **分支是 41 字节的文件** | 创建分支 = 写一个 hash 到文件 |

---

## 6. 为什么 Git 这么可靠？

- **SHA-1 哈希校验**：每个对象的名字就是它的内容哈希。内容被篡改 → hash 对不上 → Git 会发现。
- **不可变性**：一旦创建，commit 对象不会再被修改。rebase/reset 创建新 commit，旧的不动。
- **分布式**：每个人有完整副本。GitHub 挂了？任何人的 clone 都能恢复。

---

## 7. 从对象模型回看所有操作

学习了 Git 内部后，回顾所有操作：

| 操作 | 在对象模型层面做了什么 |
|------|----------------------|
| `git add` | 创建 blob 对象，更新 index（暂存区） |
| `git commit` | 创建 tree + commit 对象，更新 ref |
| `git branch` | 在 `.git/refs/heads/` 下创建一个文件 |
| `git checkout` | 读取 commit → tree → blob，还原到工作区；更新 HEAD |
| `git merge` | 创建新的 commit 对象（有两个 parent） |
| `git rebase` | 创建新的 commit 对象（新 parent），移动 ref |
| `git reset` | 移动 ref 和 HEAD |
| `git push` | 把本地 objects 和 refs 发送到远程 |

> 所有「高级」操作，本质上都是在**创建对象**或**移动指针**。

---

## 8. 你学到了什么

| 概念 | 一句话 |
|------|--------|
| Git = 内容寻址文件系统 | 用 SHA-1 哈希作为文件名存储对象 |
| blob | 文件内容 |
| tree | 目录快照（blob 的集合 + 文件名） |
| commit | 时间树节点（tree + parent + 元信息） |
| ref | 指向 commit 的人类可读标签（分支/标签） |
| `git cat-file -p` | 偷看 Git 对象 |
| 为什么快 | 快照 + 内容去重 + 本地操作 |
| 为什么可靠 | SHA-1 校验 + 不可变性 + 分布式 |

---

## 9. 自己动手

1. **在 `.git/objects/` 里找一个对象**，用 `git cat-file -p` 查看
2. **追踪一个 commit**：从 `git log` 拿到 hash → `git cat-file -p` 看 commit 对象 → 拿到 tree hash → `git cat-file -p` 看 tree 对象 → 拿到 blob hash → `git cat-file -p` 看文件内容
3. **打开 `.git/refs/heads/main`**：看里面写了什么
4. **打开 `.git/HEAD`**：看里面写了什么
5. **对比 git log 和 .git/refs 里的内容**——理解 ref 就是「指针」

---

> **恭喜！你已完成了 s23 的全部课程。**
>
> 从 s00 的「心智模型」到 s12 的「内部原理」，你现在不仅会用 Git，而且真正理解了 Git。
> 回到 [s23 主页](../README.md) 复习，或者去实际项目中运用这些知识。
