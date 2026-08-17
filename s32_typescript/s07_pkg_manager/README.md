# s32-07: npm / pnpm — 把别人的代码装进自己的项目

[← 返回概览](../README.md) | [上一章：Node.js](../s06_node/) | [下一章：泛型](../s08_generics/)

> 一句话核心思想：**包管理器解决「依赖地狱」：声明需要什么（package.json），锁定装了什么（lock 文件），自动放进 node_modules。**

---

## 问题 — 为什么需要包管理器？

自己写代码总有写不完的部分：彩色输出、命令行参数解析、日期处理……难道每个都从零写？当然不——npm 生态有 200 万+ 现成的包。但直接"下载 zip 复制进项目"会遇到三个问题：

1. **依赖的依赖**：chalk 依赖别的包，别的包又依赖更底层的包——手动复制要疯
2. **版本冲突**：A 包要 lodash 4，B 包要 lodash 3，怎么办？
3. **团队一致性**：你装的 v1.2.3，同事装的 v1.9.0，bug 只在一个人电脑上出现

包管理器就是解决这三件事的工具。

---

## 原理 — 一句话 + 示意图

**package.json 声明依赖 → npm/pnpm 解析依赖树 → node_modules 落地 → lock 文件锁定结果。**

```
你写:  package.json 依赖 chalk ^5
        │
        ▼
npm install
        │  解析 chalk 5 的依赖树
        ▼
node_modules/
├── chalk/            ← chalk 本体
└── ...               ← chalk 的依赖（npm: 平铺在这里；pnpm: 符号链接）
        │
        ▼
package-lock.json  ← 锁定精确版本，下次 install 一模一样
```

---

## 核心概念 — 分点讲解

### 1. package.json 关键字段

| 字段 | 管什么 | 本模块的值 |
|---|---|---|
| `name` / `version` | 包的身份 | s32-typescript / 私有 |
| `type` | 模块系统（`module` = ESM，s05） | `"module"` |
| `engines` | 要求的环境 | `node >=22.18` |
| `scripts` | 常用命令快捷键 | `typecheck`、`demo:s13` |
| `dependencies` | 运行时依赖 | （无） |
| `devDependencies` | 仅开发时依赖 | typescript、@types/node、chalk |

### 2. semver：版本号的三段式

```
^5.4.0   →  5.x.x（允许次版本/补丁更新）← 默认推荐
~1.2.3   →  1.2.x（只允许补丁更新）
1.2.3    →  精确锁定
```

**大版本变化 = 不兼容**（破坏性变更），所以 `^` 让你自动拿 bug 修复和新功能，又不会被大版本坑。**lock 文件锁住精确版本**，保证所有人装出来一模一样——必须提交进 git。

### 3. npm vs pnpm

| | npm | pnpm |
|---|---|---|
| node_modules | 平铺复制 | 符号链接 |
| 磁盘占用 | 每个项目一份 | 全局 store 存一份，项目里是链接 |
| 幻影依赖 | 可能（能 import 未声明的包） | 没有（严格隔离） |
| 速度 | 一般 | 快（硬链接免复制） |

**幻影依赖**：npm 平铺后，你能 `import` 到没写进 package.json 的包——某天依赖树一变化，代码就炸。pnpm 的严格布局让你只能用声明过的依赖。

> ⚠️ **同一项目不要 npm/pnpm 来回 install**——两种布局会互相污染 node_modules。选一个用到底。

### 4. 装包看三点

1. **模块系统**：包是 ESM-only 还是 CJS（chalk v5 是 ESM-only，CJS 项目只能装 v4）
2. **维护状态**：最近更新时间、issue 数量
3. **包大小与依赖数**：`npm install` 时看装了多少东西

---

## 跟 Agent 的关系 — 连接到 Claude Code

Claude Code 本身是一个发布在 npm 上的包（你可能是 `npm install -g @anthropic-ai/claude-code` 装的）：

- 它的 package.json 里 dependencies 就是它的全部"家当"
- 它的 lock 文件保证每个人装的 Claude Code 行为一致
- 它打包发布到 npm registry → 你 install → bin 链接到全局命令 `claude`

**本章学的就是「如何装 Claude Code」的机制本身。** 学完你也能把自己的 CLI 工具发布成 npm 包。

---

## 试一下

```bash
node s32_typescript/s07_pkg_manager/code.ts

# 实验 1：用 pnpm 体验符号链接布局（建议用个临时目录试）
mkdir /tmp/pnpm-demo && cd /tmp/pnpm-demo && pnpm init -y && pnpm add chalk
ls -la node_modules            # 看到符号链接了吗？
pnpm store path                # 全局仓库在哪？
cd .. && rm -rf /tmp/pnpm-demo

# 实验 2：npm view chalk version 看最新版本；npm view chalk dependencies 看它的依赖
# 实验 3：把自己想象成一个包：新建目录 → package.json 加 "bin" 字段 → npm link
```

---

## 小结 — 记住这个就够了

1. **package.json 声明，lock 文件锁定，node_modules 落地**——三件套缺一不可
2. **`^` 允许次版本更新，大版本变化 = 不兼容**；lock 文件必须进 git
3. **npm 平铺复制，pnpm 符号链接**——pnpm 快且省磁盘，还能防幻影依赖
4. **装包前看模块系统**：ESM-only 的包（chalk v5）在 CJS 项目里用不了
5. **别 npm/pnpm 混用**
