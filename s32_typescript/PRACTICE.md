# s32 TypeScript 实战练习 — 总索引

> **只看不写 = 白看。** 每一章学完，打开对应章节的 `practice.md`，挑一个需求动手写，跑通、通过 typecheck，再学下一章。

---

## 怎么用（三步）

```
① 学完一章教程（README + 跑 code.ts）
        │
        ▼
② 打开该章 practice.md，按难度挑需求
        │   每个需求都有：背景 / 验收标准 / 技术要点 / 超纲提示 / 自测方法
        ▼
③ 在章节目录里写 practice_xxx.ts，跑通 + typecheck 通过
        │
        ▼
④ 勾选 ✅，进入下一章（技能滚雪球，后面章节的需求会用到前面所有技能）
```

- **只给需求和提示，不给完整答案**——卡住了回到主项目提问，或回看该章 README
- 解答文件放章节目录内，命名 `practice_<名字>.ts`；想集中管理也可以建 `practice/` 目录，用相对导入即可

## 核心约定（写代码时必读）

| 约定 | 说明 |
|---|---|
| **node 直跑** | `node s32_typescript/sXX_xxx/practice_xxx.ts`，Node 22.18+ 自动擦除类型，零构建 |
| **导入带 `.ts`** | 相对导入必须带扩展名：`import { x } from "../xxx.ts"` |
| **路径用 dirname** | 涉及文件路径一律 `import.meta.dirname`，别依赖 `process.cwd()` |
| **可擦除语法** | 避开 enum / namespace / 参数属性 / 装饰器（s13 是唯一例外，需要编译） |
| **质检员** | `cd s32_typescript && npm run typecheck` 必须零报错 |

## 难度说明

- ⭐ **入门**：把本章例子换个场景重做一遍，巩固概念
- ⭐⭐ **组合**：跨前面章节，练真实的小系统
- ⭐⭐⭐ **挑战**：超纲内容（🔧 需要查文档、引新库），想深挖才做，不做不影响进度

## 技能依赖链

每个需求标注"前置技能：s01~sXX"，意思是：**学到第 XX 章时，前面所有技能你都已经会了**，需求只会用这些技能（超纲点已单独标注 🔧）。

```
s01 基础语法 ──► s02 interface/type ──► s03 union/narrowing ──► s04 async
      │                │                     │                     │
      ▼                ▼                     ▼                     ▼
s05 es_module ──► s06 node ──► s07 npm/pnpm ──► s08 泛型 ──► s09 class ──► s10 错误处理
      │                │                     │                     │
      ▼                ▼                     ▼                     ▼
s11 文件系统/subprocess ──► s12 高级类型 ──► s13 装饰器 ──► s14 Compiler API ──► s15 类型体操
                                                                              │
                                                                              ▼
                                                     s16 综合实战：HTTP API 服务器
```

## 全章节需求速览

| 章 | 需求 1（⭐ 入门） | 需求 2（⭐⭐ 组合） | 需求 3（⭐⭐⭐ 挑战） |
|---|---|---|---|
| [s00](s00_mental_model/practice.md) | 热身：给 JS 代码贴标签 | — | — |
| [s01](s01_ts_basics/practice.md) 基础语法 | 命令行 BMI 计算器 | 记账小本本（内存版） | 外部输入守卫 |
| [s02](s02_interface_type/practice.md) interface/type | 学生登记表 | 配置加载器 | 给第三方类型打补丁 |
| [s03](s03_union_narrowing/practice.md) union/narrowing | 命令分发器 | 表单校验器 | 图形面积/周长计算器 |
| [s04](s04_async/practice.md) async | 模拟下载器（串行 vs 并行） | 请求超时器与批量结果 | 并发任务调度器 |
| [s05](s05_es_module/practice.md) ES Module | 模块化重构 BMI 计算器 | 插件注册表 | CJS/ESM 桥 |
| [s06](s06_node/practice.md) Node.js | 环境变量配置检查器 | 迷你 JSON API | 静态文件服务器 |
| [s07](s07_pkg_manager/practice.md) npm/pnpm | chalk 上色 CLI | 发布第一个 CLI | 依赖健康检查器 |
| [s08](s08_generics/practice.md) 泛型 | 泛型工具集 | 泛型缓存 Cache\<T\> | 类型安全 API 客户端 |
| [s09](s09_class/practice.md) class | 钱包类 | 图形类层次（抽象类） | 任务队列类 |
| [s10](s10_error_handling/practice.md) 错误处理 | 错误家族 | Result 化改造 | 重试器 |
| [s11](s11_fs_process/practice.md) 文件系统 | 目录树浏览器 | 批量重命名工具 | Markdown 笔记工具 |
| [s12](s12_advanced_types/practice.md) 高级类型 | getProp 安全取值 | 手写工具类型 + satisfies | 类型安全事件表 |
| [s13](s13_decorator/practice.md) 装饰器 | @log/@measure/@memo | @route 迷你框架 | 简易 DI 容器 |
| [s14](s14_compiler_api/practice.md) Compiler API | 代码统计器 | TODO/FIXME 扫描器 | 导出清单生成器 |
| [s15](s15_type_gymnastics/practice.md) 类型体操 | 手写工具类型库（带测试） | 类型安全路由 | 类型层计算器 |
| [s16](s16_capstone/practice.md) 综合实战 | 扩展 todo：priority+筛选 | 并发安全与压测 | 第二个完整 API |

## 学习节奏建议

- **每章至少做需求 1**（⭐），做完再学下一章——"会了"的定义是能写出来，不是看懂了
- 时间紧就只做 ⭐；⭐⭐ 是真实小系统的感觉，值得做；⭐⭐⭐ 留给想深挖或面试准备
- 每 4 章（s01~s04 / s05~s08 / s09~s12 / s13~s16）是一个阶段，做完回头把前面 ⭐ 需求重写一遍，体会"手感"的变化
- 全部做完后：s16 需求 3（第二个完整 API）就是对整个模块的最终检验

## 卡住了怎么办

1. 回看本章 README（概念、原理、小结）
2. 看该章 code.ts（教学代码就是最好的"半答案"）
3. 拆解问题：把需求拆成 3 个小步骤，先跑通最小版本再叠加
4. 回到主项目提问（把需求 + 你写到哪一步 + 报错贴出来）
