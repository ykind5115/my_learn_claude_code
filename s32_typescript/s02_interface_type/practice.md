# s32-02: interface / type — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话本章核心思想：**interface 是「形状契约」，type 是「标签的别名」——两者 90% 场景通用，差异只在扩展方式。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s02（基础语法 + interface/type）
- 自测方式：`node s32_typescript/s02_interface_type/practice_xxx.ts` 从仓库根直跑看输出；`cd s32_typescript && npm run typecheck` 零报错
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`

## 需求 1：学生登记表（⭐ 入门 | 核心技能：interface 设计、可选/readonly/索引签名）
- [ ] 完成

### 背景
interface 是对象形状的图纸，用小系统把图纸用熟——可选、readonly、索引签名是形状的「三件套」，一个登记表全碰到。

### 要做什么（验收标准）
1. 定义 `interface Student { readonly id: string; name: string; age?: number; email?: string; scores: Record<string, number> }`。
2. 写 `addStudent` / `listStudents` / `findByName` / `findByEmail`，参数、返回值全部用 Student 契约标注。
3. 用 `// @ts-expect-error` 演示给 `readonly` 的 `id` 赋值时 tsc 报错（typecheck 时"预期内跳过"，node 直跑照常执行）。
4. 演示**结构化类型**：一个多带了字段（如 `address`）的对象也能传进 `findByName`——不用 extends。
5. typecheck 零报错。

### 技术要点
- 可选属性 `?` = "这个字段可能不存在"，省掉到处写 `undefined` 检查
- `readonly` = 编译期封条：创建后不可改（运行时其实能改，标签擦除后没人管——但它把意图写成了契约）
- `Record<string, number>` = 索引签名的语法糖：任意课程名 → 分数
- 结构化类型（鸭子类型）：形状对得上就兼容，不需要登记身份——接口是「需求清单」不是「身份证」
- `@ts-expect-error` = 下一行有类型错误（我故意的），typecheck 跳过、node 直跑照常——浓缩了「类型错误只挡编译期」

### 超纲提示
🔧 `Record<K, V>` 是内置泛型工具（s08 讲原理），先用起来；想进一步收口，可以试试 `Partial<Student>`（s08 展开）——它让"只改部分字段"的更新函数签名更诚实。

### 自测方法
```bash
node s32_typescript/s02_interface_type/practice_students.ts   # 添加/列出/查找全跑一遍
cd s32_typescript && npm run typecheck                        # 零报错（@ts-expect-error 处除外）
# 实验 1：故意给 Student 少写一个 name，typecheck 看「缺字段」报错
# 实验 2：把 @ts-expect-error 删掉，typecheck 看 readonly 报错
```

## 需求 2：配置加载器（⭐⭐ 组合 | 核心技能：interface + 函数类型成员 + 默认值合并）
- [ ] 完成

### 背景
真实程序都从配置开始：用户给一部分、系统补默认值。「接口 + 默认值合并」是通用模式，也是 s16 写 HTTP 服务器前必练的一手。

### 要做什么（验收标准）
1. 定义 `interface AppConfig { host: string; port: number; retry?: number; timeout?: number; onError?: (msg: string) => void }`。
2. `loadConfig(partial: Partial<AppConfig>): AppConfig`——**手写合并逻辑**，把默认值（如 `{ retry: 3, timeout: 5000, onError: ... }`）和传入的 partial 合并。
3. 非法 `port`（负数 / 非整数）：抛错或返回错误，二选一，但行为要可自测。
4. 演示 `onError` 这个函数类型成员被调用：`loadConfig({ onError: (m) => console.log(m) }).onError?.("出错了")`。
5. 空配置 / 部分配置 / 非法 port 三组数据，typecheck 零报错。

### 技术要点
- interface 里的**函数类型成员**：`onError?: (msg: string) => void`——回调也纳入契约
- `Partial<AppConfig>` = 所有字段变成可选的映射（s08 讲原理，先用起来）
- 展开运算符合并：`{ ...defaults, ...partial }`——后写的覆盖先写的
- 契约型数据显式标注：`loadConfig` 的参数、返回都写上 interface，调用方不用猜
- 项目约定三件套：相对导入带 `.ts` 扩展名（如 `import { defaults } from "./defaults.ts"`）；文件路径一律 `import.meta.dirname`；只用可擦除语法（interface 是纯类型，天然可擦除）

### 超纲提示
🔧 配置校验的更优写法是 `satisfies` 关键字（s12 内容）——先知道名字：它能"校验字面量但保留精确类型"。

### 自测方法
```bash
node s32_typescript/s02_interface_type/practice_config.ts
# 空配置 → 全默认值；部分配置 → 默认值被覆盖；port: -1 / 1.5 → 报错
cd s32_typescript && npm run typecheck
```

## 需求 3：给"第三方库"打类型补丁（⭐⭐⭐ 挑战 | 核心技能：声明合并）
- [ ] 完成

### 背景
真实工程天天给库的类型打补丁——不改库代码，扩展它的类型。理解了声明合并，就理解了 interface 存在的意义之一。

### 要做什么（验收标准）
1. 模拟"第三方库"：`interface Logger { log(msg: string): void }` + 一段使用它的代码。
2. 用**同名声明** `interface Logger { level: "debug" | "info" | "error" }` 扩展所有 Logger 实例——补丁后，`logger.level` 能读、能比较，类型检查生效。
3. 演示补丁后类型检查生效（`logger.level` 的类型是字面量联合，不是 `string`）。
4. 对照实验：同名 `type` 声明两次 → tsc 报「Duplicate identifier」。
5. typecheck 通过；故意写错补丁字段（如 `level: "verbose"` 之外的类型）看报错。

### 技术要点
- **同名 interface 自动合并**：第二次声明是"补丁式"扩展，所有 Logger 实例立刻多出 `level`
- 声明合并 vs type：`type` 同名声明两次报错，`interface` 合并——这就是打补丁场景为什么用 interface
- 判别字段配合字面量联合：`level: "debug" | "info" | "error"` 让日志分级也能被穷尽检查（s03 内容，可先感受）
- 只用可擦除语法（interface 是纯类型，天然可擦除）

### 超纲提示
🔧 查 "declaration merging module augmentation"——模块化声明合并，真实 `@types` 包给第三方库打补丁的写法（`declare module "xxx" { interface ... }`）。

### 自测方法
```bash
cd s32_typescript && npm run typecheck     # 通过
# 实验 1：把第二个 interface 改成 type，typecheck 看「Duplicate identifier」报错
# 实验 2：把补丁字段改成错误的类型（如 level: "verbose"），看哪里变红
node s32_typescript/s02_interface_type/practice_patch.ts     # 直跑，类型被撕掉、运行不受影响
```

## 做完之后
- 自查：你用了本章哪些概念？（interface 设计 / 可选 ? / readonly / 索引签名 / 函数类型成员 / Partial / 展开合并 / 结构化类型 / 声明合并）
- 想继续深挖：回看本章 README 的「跟 Agent 的关系」——MCP 协议的类型就是 interface 契约，试着用声明合并给 `McpTool` 补一个自定义字段
