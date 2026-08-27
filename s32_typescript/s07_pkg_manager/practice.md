# s32-07: npm / pnpm — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话本章核心思想：**包管理器解决「依赖地狱」：声明需要什么（package.json），锁定装了什么（lock 文件），自动放进 node_modules。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s07（会用到 s05 的 BMI 计算器、s06 的环境检查器）
- 自测方式：`cd s32_typescript && npm install` 装好依赖；`node s32_typescript/s07_pkg_manager/<文件名>.ts` 直跑；`cd s32_typescript && npm run typecheck` 零报错；需求 2 用全局命令 `mycli` 自测
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`；需求 2 要新建独立的 `my-cli/` 小项目（自带 package.json）
- ⚠️ 开工前先 `cd s32_typescript && npm install`（README：只有 s07/s13/s14 需要依赖）；本模块用 npm 就不要切 pnpm 重装——两种 node_modules 布局会互相污染

## 需求 1：给 s01 BMI 计算器上色（⭐ 入门 | 核心技能：装依赖 + 用 ESM-only 包（chalk））
- [ ] 完成

### 背景
chalk 是第一个第三方依赖的最佳练手对象：装包、读文档、用 API 一次练完，而且立刻有肉眼可见的效果。README 说"学完你也能把自己的 CLI 发布成 npm 包"——第一步就是会用别人的包。

### 要做什么（验收标准）
1. 确认依赖已装：`cd s32_typescript && npm install`（chalk 在 devDependencies 里，装完后 `node_modules/chalk` 存在）
2. 把 s05 需求 1 的 BMI 计算器输出上色：正常（18.5≤BMI<24）绿、偏瘦黄、偏胖红——分别用 `chalk.green(...)` / `chalk.yellow(...)` / `chalk.red(...)`
3. 再挑一个小 CLI 上色（比如 s06 需求 1 的环境检查器：`[MISSING]` 红色、`✅` 绿色）
4. 上色版 typecheck 零报错
5. 观察 `package.json`：确认 `chalk` 出现在 devDependencies，版本带 `^`

### 技术要点
- **npm install 流程**：`npm install` 按 package.json 声明装依赖 → 生成/更新 `package-lock.json`（README 原理图的三件套）
- **chalk 是 ESM-only**：chalk v5 只能用 `import`，本项目的 `"type": "module"` 正好兼容；**CJS 项目只能装 v4**——"装包看三点"第一点就是模块系统（README 核心概念 4）
- **package.json 字段变化**：装包后观察 dependencies / devDependencies 的区别（README 核心概念 1 的表）
- **颜色选择与业务逻辑分离**：分类函数（classifyBmi）不该 import chalk，颜色映射放 CLI 层——s05 的职责边界又用上了
- 复用 s05 的 `bmi-lib.ts` 时用相对导入：`import { classifyBmi } from "../s05_es_module/bmi-lib.ts"`（带 `.ts` 扩展名，跨目录也一样）

### 超纲提示
🔧 看 `node_modules/chalk/package.json` 的 `exports` 字段——它声明了这个包对外提供哪些入口、是 ESM 还是 CJS。读懂了它，你就理解了"模块系统声明"长什么样（s05 判定规则在真实包上的体现）。

### 自测方法
```bash
cd s32_typescript && npm install
node s32_typescript/s07_pkg_manager/practice_bmi_color.ts 170 65   # 正常 → 绿色
node s32_typescript/s07_pkg_manager/practice_bmi_color.ts 170 50   # 偏瘦 → 黄色
node s32_typescript/s07_pkg_manager/practice_bmi_color.ts 170 80   # 偏胖 → 红色
cd s32_typescript && npm run typecheck
# 如果 bmi-lib.ts 里还留着 s05 的顶层 console.log，它会打印一次——模块缓存再次生效，不用管它
# 实验：把输出重定向到文件（> out.txt），ANSI 色码会以转义序列原样出现——这就是颜色的底层真相
```

## 需求 2：发布第一个 CLI（⭐⭐ 组合 | 核心技能：package.json bin + npm link）
- [ ] 完成

### 背景
README 的"跟 Agent 的关系"说：Claude Code 就是 npm 包 + bin 链接到全局命令 `claude`。"学完你也能把自己的 CLI 发布成 npm 包"——这题就是这句话的落地：不用真的发布到 npm registry，`npm link` 就能让你在任意目录敲自己的命令。

### 要做什么（验收标准）
1. 在本章目录下新建 `my-cli/`：
   - `package.json`：`name`（如 `my-cli`）、`version`（如 `0.1.0`）、`bin: { "mycli": "cli.ts" }`
   - `cli.ts`：`#!/usr/bin/env node` shebang 开头，打印问候语 + 版本号，读 `process.argv` 支持可选参数
2. `cd my-cli && npm link`：把命令链接到全局
3. **任意目录**敲 `mycli` 能跑（新开一个终端，`cd` 到别处再敲）
4. `npm unlink` 清理（在 my-cli 目录里），验证 `mycli` 已不可用
5. **两种 bin 姿势都试**：Node 22.18+ 理论上能直接以 .ts 作为 bin 入口（type stripping）；如果 `mycli` 报错跑不起来，就 `tsc` 编译成 .js 再把 bin 指向 .js。把实测结论（哪种成功、报错长什么样）写进 `my-cli/NOTES.md`
6. typecheck 零报错（`my-cli/cli.ts` 会被根目录的 tsc 一起检查）

### 技术要点
- **bin 字段映射命令名 → 文件**：`"bin": { "mycli": "cli.ts" }` 表示全局命令 `mycli` 执行这个文件（README 实验 3）
- **npm link 原理**：在全局 node_modules 里建一个符号链接指向你的 my-cli——改代码立刻生效，不用重新装
- **shebang**：`#!/usr/bin/env node` 让操作系统知道用 node 解释这个文件；Windows 上 npm 生成的 `.cmd` 垫片也依赖它
- **npm unlink 清理**：做完要拆掉，别留全局垃圾
- my-cli 是独立包：有自己的 package.json，和 s32 根项目互不干扰；但文件在仓库里会被根 tsc 检查，所以也要过 typecheck

### 超纲提示
🔧 `npm pack` / `npm publish --dry-run` 看包内容——它会按 package.json 的 `files` 字段（或默认规则）打包，`--dry-run` 不真发，只列出包里会有什么。看看你的 cli.ts 有没有被打进去。

### 自测方法
```bash
cd s32_typescript/s07_pkg_manager/my-cli
npm link
# 新开一个终端（任意目录）：
mycli                       # 应打印问候 + 版本
mycli 张三                  # 应打印带参数的问候
# 回到 my-cli 目录清理：
npm unlink
# 再新开终端敲 mycli → 应提示找不到命令
cd s32_typescript && npm run typecheck
```

## 需求 3：依赖健康检查器（⭐⭐⭐ 挑战 | 核心技能：读 package.json + semver 理解）
- [ ] 完成

### 背景
README 把 semver 三段式讲得很清楚，这题把它变成工具：扫一遍项目的 package.json 和 node_modules，检查"声明的范围 vs 实际装的版本"是否一致，顺手把 npm 平铺带来的幻影依赖揪出来。做完这个工具，semver 的 `^` 和 `~` 就不只是概念，而是你手写过的逻辑。

### 要做什么（验收标准）
1. `depcheck.ts`（放本章目录）：
   - 用 `node:fs` 读 `s32_typescript/package.json`（路径基于 `import.meta.dirname` 定位；fs 是 s11 前瞻）
   - 用 `fs.readdir` 扫 `s32_typescript/node_modules/` 下每个顶级目录，读各自的 `package.json` 拿实际安装的 `version`
2. 对每个声明在 dependencies / devDependencies 里的条目：
   - 解析声明的范围（`^5.4.0` / `~1.2.3` / `1.2.3` / `*`），按 semver 语义判断实际版本是否在范围内
   - 在范围内 → `✅ name@实际版本（声明 ^5.4.0）`；不在 → `⚠️ 版本不在范围内`
3. 未声明的顶级依赖（出现在 node_modules 顶层但不在 package.json 里）→ `⚠️ 幻影依赖: name@version`
4. 输出格式清晰，最后给总结行（几个 ✅ / 几个 ⚠️）
5. typecheck 零报错

### 技术要点
- **JSON 读取（s11 前瞻）**：`readFileSync` + `JSON.parse`，或 `fs/promises` 的异步版——先照猫画虎用起来
- **semver 三段式解析**：把 `5.4.0` 拆成 `{ major: 5, minor: 4, patch: 0 }`，比较时先比 major、再比 minor、再比 patch（README 核心概念 2）
- **^ 和 ~ 的语义实现**：`^5.4.0` = 同 major（≥5.4.0 且 <6.0.0）；`~1.2.3` = 同 major.minor（≥1.2.3 且 <1.3.0）；精确 `1.2.3` 只认这一个；`*` 全收
- **幻影依赖**：npm 平铺把传递依赖也放 node_modules 顶层，你能 import 到没声明过的包——扫描把它们标出来（README 核心概念 3 的 npm vs pnpm 表）
- 手写解析要先处理边界：范围里有空格、版本是 `0.x`、声明了但 node_modules 里没装——都要有明确输出

### 超纲提示
🔧 直接 `npm install semver` 装上官方库，和你的手写版跑同一份数据对比结果——官方实现会处理更多边界（prerelease、range 组合），这正是"别重复造轮子"的活教材。

### 自测方法
```bash
cd s32_typescript && npm install
node s32_typescript/s07_pkg_manager/depcheck.ts
# 应看到：chalk / typescript / @types/node 全 ✅（按实际版本），
#         以及若干 ⚠️ 幻影依赖（npm 平铺的传递依赖，如 undici-types 之类）
# 实验 1：把根 package.json 里 typescript 的 "^5.8.0" 临时改成 "^4.0.0"，再跑 → 应出现 ⚠️ 版本不在范围内；测完改回来
# 实验 2：npm ls --depth=0 对比你的扫描结果，看官方怎么看顶级依赖
cd s32_typescript && npm run typecheck
```

## 做完之后
- 自查：你用了本章哪些概念？——npm install 与 lock 文件、dependencies vs devDependencies、semver 三段式与 ^ / ~ / 精确、ESM-only 包、bin + npm link、幻影依赖
- 想继续深挖：回看本章 README 的"跟 Agent 的关系"，选一个点展开——比如用需求 2 的方法把"环境检查器"打包成全局命令，或者研究 lock 文件里一个真实依赖的解析记录，看懂 npm 是怎么帮你决定装哪个版本的
