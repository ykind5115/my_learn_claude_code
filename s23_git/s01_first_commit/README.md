# s01: 第一次提交 — 种下时间树的第一个节点

[s00](../s00_mental_model/) → `s01` → [s02](../s02_browsing_history/) → ... → s12
> *"三行命令，让 Git 开始记录你的项目历史。"*
>
> **前提知识**: 看过 s00（知道 commit = 时间线上的节点、知道三个区域是什么）。会打开终端。

---

## 1. 为什么需要 git init / add / commit？

回顾 s00 的那张图：

```
工作区  →  暂存区  →  仓库（时间树）
```

如果你什么都不做，你的项目文件夹就是一个**普通文件夹**——和 Git 没有任何关系。里面改了文件、删了文件，没有任何记录。

**这三个命令各自解决一个问题**：

| 命令 | 解决的问题 |
|------|-----------|
| `git init` | "怎么告诉 Git 开始管理这个文件夹？" |
| `git add` | "这些改动中，哪些要放进下一次快照？" |
| `git commit` | "按下快门，在时间树上种一个新节点" |

---

## 2. 在时间树模型下理解这三个命令

用 s00 的时间树模型来看：

```
                         git add
    工作区              ──────────→              暂存区
    (你编辑的文件)      ←──────────              (选中要拍的文件)
                         git restore --staged

                         git commit
    暂存区              ──────────→              仓库（时间树）
    (选中要拍的文件)                               (历史快照)
                         git reset HEAD~


    工作区 ── git add ──→ 暂存区 ── git commit ──→ 时间树

    0. 初始状态:  一棵「空的时间树」（没有任何节点）
    1. git add:   把文件标记为「要拍」
    2. git commit: 种下第一个节点！树不再空了。
```

---

## 3. 怎么做 — 逐行解释

### 3.1 `git init` — 创建一棵空的时间树

```bash
mkdir my-project
cd my-project
git init
```

输出：
```
Initialized empty Git repository in /path/to/my-project/.git/
```

**发生了什么？**

Git 在你的项目文件夹里创建了一个隐藏目录 `.git/`。这个目录就是**时间树本身**——所有的快照、分支、标签、历史，全存在这里。

```
my-project/
├── .git/           ← 这就是整棵时间树！
│   ├── objects/    ← 存放所有快照（blob、tree、commit 对象）
│   ├── refs/       ← 存放分支和标签指针
│   ├── HEAD        ← 「你现在在哪」的指针
│   └── ...
└── (你的文件 — 工作区，还是空的)
```

> **关键理解**：删除 `.git/` 目录 = 删除所有 Git 历史。你的文件还在，但时间树没了。

### 3.2 `git config` — 给树签名

在第一次提交之前，告诉 Git 你是谁：

```bash
git config user.name "你的名字"
git config user.email "your@email.com"
```

这个信息会被写入每个 commit 节点——谁创造了这个节点。

> 如果跳过这步直接 commit，Git 会报错并提示你先配置。也可以用 `--global` 全局配置一次：
> ```bash
> git config --global user.name "你的名字"
> git config --global user.email "your@email.com"
> ```

### 3.3 创建文件 → 工作区有了内容

```bash
echo "# 我的项目" > README.md
```

此时：
- **工作区**：有了 `README.md`
- **暂存区**：空的
- **仓库**：空的（时间树还没有节点）

### 3.4 `git add` — 把文件放进准备区

```bash
git add README.md
```

**发生了什么？**

Git 把 `README.md` 的当前内容复制到暂存区。暂存区现在说：「下次拍照时，把这个文件拍进去。」

**时间树模型视角**：你正在选择「下一个节点的快照里要包含哪些文件」。

> `git add .` 表示把当前目录下所有改过的文件都加入暂存区。`. ` 代表「当前目录下所有文件」。

### 3.5 `git commit` — 种下第一个节点！

```bash
git commit -m "第一次提交：创建 README"
```

输出：
```
[master (root-commit) a1b2c3d] 第一次提交：创建 README
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

**发生了什么？** Git 做了 5 件事：

```
① 给暂存区里的所有文件拍一张快照
② 创建一个 commit 节点，写入:
   - 快照内容（README.md 的完整内容）
   - 作者信息（刚才 config 的 name + email）
   - 时间戳
   - 提交信息："第一次提交：创建 README"
   - parent 指针 → 因为这是第一个 commit，没有 parent（叫 root-commit）
③ 把节点存入 .git/objects/
④ 把 HEAD 和分支标签指向这个新节点
⑤ 清空暂存区（准备下一次提交）

完成后的时间树:

    ●  a1b2c3d  ← main (HEAD)
       "第一次提交：创建 README"
```

> `-m` 是 message 的缩写。如果不用 `-m`，Git 会打开默认编辑器让你写提交信息。新手建议先用 `-m`，信息写在一行内。

### 3.6 `git log` — 查看时间线

```bash
git log
```

输出：
```
commit a1b2c3d4e5f6... (HEAD -> main)
Author: zhangsan <zhangsan@example.com>
Date:   Sun Jun 29 15:30:00 2026 +0800

    第一次提交：创建 README
```

---

## 4. 再做两次提交，感受时间树的生长

```bash
# 第二次提交
echo "版本: 1.0.0" >> README.md
git add README.md
git commit -m "添加版本号"

# 第三次提交
echo "作者: zhangsan" >> README.md
git add README.md
git commit -m "添加作者信息"
```

三次提交后，时间树长这样：

```
    ●  a1b2c3d  ← 第一个 commit（根节点）
    │     "第一次提交：创建 README"
    │
    ●  b2c3d4e  ← 第二个 commit
    │     "添加版本号"
    │
    ●  c3d4e5f  ← 第三个 commit  ← main (HEAD)
          "添加作者信息"

HEAD → main → 最新的 commit
```

> 每次 commit，当前分支标签（main）自动移动到新节点。HEAD 跟着一起走。

---

## 5. 常见错误（新手必读）

### ❌ 错误 1：`git add` 之后又改了文件，然后 `git commit`

```bash
# 你做了:
git add README.md        # 暂存区保存了 README 的「版本1」
# 然后又改了 README.md   # 工作区现在是「版本2」
git commit -m "xxx"      # 提交的是暂存区里的「版本1」！

# 工作区的「版本2」没有被提交，还在那等着。
# 修复: 再 git add + git commit 一次
```

> **规则**：`git commit` 只提交**暂存区里的内容**，不管你工作区有什么。每次修改后如果想提交，必须先 `git add`。

### ❌ 错误 2：忘记 `git add` 直接 `git commit`

```bash
git commit -m "改了东西"
# 输出: nothing to commit, working tree clean
# 原因: 暂存区是空的——你改了文件但没 add
```

### ❌ 错误 3：提交信息写「修改」或「update」

```
❌ 坏的提交信息:
  "修改"
  "update"
  "修 bug"
  "."

✅ 好的提交信息:
  "修复登录按钮在 Safari 上不响应点击的问题"
  "添加用户注册时的邮箱格式校验"
```

> **规则**：提交信息应该让 6 个月后的你能看懂这个 commit 做了什么。

### ❌ 错误 4：`git init` 在已有项目的子目录里执行

```
my-project/          ← 在这里 git init ✅
  src/
  docs/

my-project/
  src/
    git init         ← ❌ 不应该在这里再 init
```

> 一个项目只需要一个 `.git/`。嵌套 init 会导致混乱。

---

## 6. 你学到了什么

| 概念 | 你具体做了什么 |
|------|---------------|
| `git init` | 在项目文件夹里创建了 `.git/`——一棵空的时间树 |
| `git config` | 设置用户名和邮箱，每个 commit 都会记录 |
| `git add` | 把文件从工作区复制到暂存区——「选这些拍」 |
| `git commit` | 拍快照，种节点，移动分支标签，清空暂存区 |
| `git log` | 查看时间线上的所有节点 |
| 时间树生长 | 每 commit 一次，树上多一个节点，分支标签往前移 |

---

## 7. 自己动手

1. **创建一个真实项目**：在你自己选的位置，`mkdir learn-git && cd learn-git && git init`
2. **做 5 次提交**：每次创建或修改一个文件，用 `git log` 观察时间树的生长
3. **用 `git log --oneline`** 试试看更简洁的输出
4. **故意不 add 就 commit**：看看 Git 说什么
5. **尝试 `git add .`**：一次添加多个文件到暂存区

---

> **下一章：[s02: 浏览历史](../s02_browsing_history/)** — 学会在时间树上自由跳转，查看任意历史版本
