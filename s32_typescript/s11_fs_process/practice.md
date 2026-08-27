# s32-11: 文件系统 / subprocess — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话核心思想：**fs/promises 读写文件、path.join 拼路径、流处理大数据、spawn 调用外部程序——这就是 Agent 的 Read/Write/Bash 工具的底层实现。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s11（fs/promises、path、流、错误处理都要能随手用）
- 自测方式：node 直跑（`node s32_typescript/s11_fs_process/practice_*.ts`）+ `cd s32_typescript && npm run typecheck`
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`
- 项目约定：路径一律 `path.join + import.meta.dirname`（绝不依赖 `process.cwd()`）；相对导入必须带 `.ts` 扩展名；只用可擦除语法

## 需求 1：目录树浏览器（⭐ 入门 | 核心技能：fs/promises + 递归 + 路径）
- [ ] 完成

### 背景
README 实验 2 的完整版——递归遍历目录是文件工具的地基（tree、lint、打包器都靠它）。README 说 Agent 的 Read 工具 ≈ readFile，而列目录就是它目录导航的那一层。

### 要做什么（验收标准）
- `tree(dir: string, prefix?: string, depth?: number): Promise<void>`，用 `readdir(dir, { withFileTypes: true })` 递归：
  - 文件：`prefix + "├── " + name`；目录：名字后加 `/`
  - 最后一个条目用 `└──`，其余用 `├──`；子目录缩进 `prefix + "│   "`（非最后）或 `prefix + "    "`（最后）
  - 目录在前、文件在后（或保持 readdir 顺序都行，但要一致）
- 支持 `--depth <n>` 参数限制深度；不传则不限
- 根路径用 `import.meta.dirname` 定位：自建一个测试目录（如 `test_tree/`，含两级子目录和几个文件）来扫；递归进子目录时参数传 `join(dir, entry.name)`，别手拼字符串

### 技术要点
- `readdir(dir, { withFileTypes: true })` 返回 `Dirent[]`，用 `dirent.isDirectory()` 判断类型——不用逐个 stat（README 核心概念 2 附近）
- 递归 + 前缀缩进：`prefix` 参数携带当前分支的画线状态，是树形输出的核心
- `join` 拼路径：自动处理平台分隔符（Windows 的 `\` / Linux 的 `/`）和 `..`（README 核心概念 2 路径铁律）
- `import.meta.dirname` = 当前文件所在目录，不随 cwd 变——本模块铁律，绝不依赖 `process.cwd()`（模块约定 4）

### 超纲提示
- 🔧 符号链接防循环：`dirent.isSymbolicLink()` 的条目用 `realpath` 判断是否已在祖先路径里，防止 `ln -s` 目录无限递归

### 自测方法
- 建议解答文件：`s32_typescript/s11_fs_process/practice_tree.ts`
- 建好 `test_tree/` 后跑 `node s32_typescript/s11_fs_process/practice_tree.ts`：输出树形，目录带 `/`
- `node s32_typescript/s11_fs_process/practice_tree.ts --depth 2`：超过 2 层的子树被裁剪
- 换个启动目录跑一次（如 `cd E:\learn-claude-code` 再从仓库根跑），确认路径不依赖 cwd
- `cd s32_typescript && npm run typecheck`：0 错误

## 需求 2：批量重命名工具（⭐⭐ 组合 | 核心技能：readdir/rename + 预览模式 + 参数数组防注入）
- [ ] 完成

### 背景
「先预览后执行」是文件工具的安全习惯——批量 rename 一次误操作就可能毁一堆文件。README 也强调参数化调用防注入，这里把「输入只当数据、不当命令」的纪律练熟。

### 要做什么（验收标准）
- `rename-tool.ts`，解析 argv（`process.argv.slice(2)`）：
  - `--match <suffix>`：只处理以该后缀结尾的文件（如 `.txt`）
  - `--prefix <p>`：目标名前加前缀（`a.txt` → `pre_a.txt`）
  - `--ext <new>`：扩展名换成新值（`.txt` → `.md`）
  - 默认**只打印** `old → new` 预览，不执行；加 `--apply` 才真正 `rename`
- 目标名已存在 → 跳过该文件并打警告（绝不覆盖）
- 操作目录：`join(import.meta.dirname, "test_rename")`（自建测试文件）
- 打印统计：共 N 个匹配、改名 M 个、跳过 K 个

### 技术要点
- `readdir` + `rename`（`node:fs/promises`）：先列目录筛匹配，再逐个改
- argv 解析：手动解析 `--flag value` 键值对和 `--apply` 开关
- 预览/执行分离：默认只打印计划，`--apply` 才动手——安全习惯（对照 README「参数化调用防注入」的精神）
- 路径一律 `join` + `import.meta.dirname`；扩展名处理用 `node:path` 的 `basename` / `extname`，别手切字符串
- 不覆盖保护：目标存在就 `continue` + 警告

### 超纲提示
- 🔧 正则做复杂规则：日期前缀（`^(\d{4}-\d{2}-\d{2})_` 提取）、编号补零（`03_`）、模板占位符（`{date}` / `{n}`）

### 自测方法
- 建议解答文件：`s32_typescript/s11_fs_process/practice_rename_tool.ts`
- 建 `test_rename/`：`a.txt b.txt c.md`，跑 `node s32_typescript/s11_fs_process/practice_rename_tool.ts --match .txt --prefix pre_ --ext .md` → 只打印 2 行预览，文件没动
- 加 `--apply` 再跑 → 用 `ls`/`Get-ChildItem` 验证 `pre_a.md pre_b.md` 生成、`c.md` 没被动
- 再跑一次预览：目标已存在 → 跳过警告
- `cd s32_typescript && npm run typecheck`：0 错误

## 需求 3：Markdown 笔记工具（⭐⭐⭐ 挑战 | 核心技能：fs 全套 + 流 + 错误处理 + 搜索）
- [ ] 完成

### 背景
s16 要做「文件 + API」应用，笔记工具是文件层最佳练手，也是第一个多命令小系统——list/new/view/search/delete 五条命令把 fs/promises 全套 API 用遍。

### 要做什么（验收标准）
- 笔记存 `join(import.meta.dirname, "notes")`（不存在就 `mkdir`，`recursive: true`）
- 命令（argv 第一个参数）：
  - `list`：列出全部笔记，显示标题 + 更新时间（`stat` 的 `mtime`）
  - `new <title>`：创建 `notes/<title>.md`，写入模板（`# <title>\n\n`）
  - `view <title>`：打印文件内容
  - `search <keyword>`：遍历全部笔记，行级匹配，输出 `文件:行号:内容`；大文件用流式读取（`createReadStream` + `for await`，`highWaterMark` 64KB，把 chunk 按行切）
  - `delete <title>`：`unlink`
- 所有 fs 错误转友好中文提示：`ENOENT` → `"笔记不存在: <title>"`，其他错误带 `err.code` 打印
- 标题/关键词都是「数据」，绝不拼进任何 shell 命令

### 技术要点
- `fs/promises` 全套：`readdir` / `readFile` / `writeFile` / `rename` / `unlink` / `stat`（README 核心概念 1：新代码默认 promises + await）
- 路径铁律：`join(import.meta.dirname, "notes", title + ".md")`——README 核心概念 2
- 流式读大文件：`createReadStream` + `for await (const chunk of stream)`，固定小块内存边读边处理（README 核心概念 3）；`readFile` 一口闷只适合小笔记
- 错误分类处理：用 `err.code`（或 s10 的 instanceof 思路）判断，`"ENOENT"` 就是「文件不存在」，转成友好文案（s10 需求 1 的知识复用）
- 相对导入带 `.ts` 扩展名（如果拆了公共模块）

### 超纲提示
- 🔧 标题提取：view 时从内容第一个 `# ` 行提取标题显示
- 🔧 大小写不敏感搜索：`keyword.toLowerCase()` 后匹配小写化的行

### 自测方法
- 建议解答文件：`s32_typescript/s11_fs_process/practice_notes.ts`
- 一轮 CRUD：
  - `node s32_typescript/s11_fs_process/practice_notes.ts new 第一篇`
  - `node s32_typescript/s11_fs_process/practice_notes.ts list`
  - `node s32_typescript/s11_fs_process/practice_notes.ts view 第一篇`
  - 写一条含「类型」的笔记 → `node s32_typescript/s11_fs_process/practice_notes.ts search 类型`
  - `node s32_typescript/s11_fs_process/practice_notes.ts delete 第一篇` → `list` 确认消失
- 操作不存在的笔记：`view 不存在` / `delete 不存在` → 输出「笔记不存在: 不存在」
- `cd s32_typescript && npm run typecheck`：0 错误
- 跑完把 `notes/` 清掉（练习「演示完擦干净」的习惯）

## 做完之后
- 自查：你用了本章哪些概念？
  - fs/promises（readdir / readFile / writeFile / rename / unlink / stat）
  - import.meta.dirname + join 路径铁律
  - 流式读取（createReadStream + for await）
  - 错误分类处理（s10 复用）
  - 参数化调用 / 输入即数据（防注入）
- 想继续深挖：回看本章 README 的「跟 Agent 的关系」——Read ≈ readFile、Write ≈ writeFile、Bash ≈ spawn；选一个点展开：比如给笔记工具加一个 `spawn` 子命令（用 git 管理 notes 目录），或把 search 升级成流式 + 正则高亮
