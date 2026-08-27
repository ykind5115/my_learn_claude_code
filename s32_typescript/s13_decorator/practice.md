# s32-13: Decorator — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话本章核心思想：**装饰器是「包装函数」的语法糖——把日志、计时、注册这类横切功能，用一行 @ 挂到类或方法上。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s13（s12 的条件类型 / infer 帮你读懂装饰器的泛型签名；装饰器语法本身是本章内容）
- 自测方式：**本章不能 node 直跑**——装饰器是不可擦除语法，必须先 tsc 编译再跑（这是本模块唯一需要编译的章节）
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`（如 `practice_log.ts`）

### 编译练习文件（两种做法，选一个）
`s13_decorator/tsconfig.json` 的 `include` 只有 `["code.ts"]`——新建练习文件后，要么把它加进 include，要么用命令行参数指定：

- **做法 A（推荐，改 tsconfig）**：把 include 改成 `["code.ts", "practice_log.ts"]`（或只留你自己的文件），然后：
  ```bash
  cd s32_typescript && npx tsc -p s13_decorator && node s13_decorator/dist/practice_log.js
  ```
  ⚠️ 每新建一个练习文件都要把它加进 include；另外 include 变了之后 `npm run demo:s13` 会连带编译你的练习文件，练习文件有编译错会拖垮演示——练完记得把 include 改回去。

- **做法 B（不改文件，命令行传参）**：不写 `-p`，直接传文件 + 编译选项：
  ```bash
  cd s32_typescript && npx tsc s13_decorator/practice_log.ts --module NodeNext --moduleResolution NodeNext --target ES2022 --strict --outDir s13_decorator/dist && node s13_decorator/dist/practice_log.js
  ```

注意：
- 练习文件**保持自包含**，不要 `import "../utils.ts"`——参照 code.ts 自带迷你打印函数（`tsc -p s13_decorator` 的 `rootDir` 只覆盖 s13_decorator，import 外部文件会报 TS6059）
- 练习文件之间互相 import 时，相对导入必须带 `.ts` 扩展名
- tsconfig 里 `experimentalDecorators: false`——用的是 TS 5.0+ **标准装饰器**语法（`context` 参数那套），别拿老教程的旧版装饰器写法来套

## 需求 1：@log / @measure / @memo 三件套（⭐ 入门 | 核心技能：方法装饰器 + 装饰器工厂 + 叠加顺序）
- [ ] 完成

### 背景
README 实验 2 的完整版。日志、计时、缓存是生产代码里出现频率最高的三个横切关注点，把它们各写成一个装饰器，你就真正理解了"包装"的本质——业务方法里一行横切代码都没有。

### 要做什么（验收标准）
1. `@log`：方法进入时打印参数，返回时打印返回值
2. `@measure(label)`：装饰器工厂，方法调用后打印耗时（label 是你传入的名字）
3. `@memo`：相同参数直接返回缓存结果（缓存 Map 放哪？——装饰器工厂的闭包就是天然缓存空间，每次工厂调用各有一份独立缓存）
4. 在 ApiService 的一个方法上叠加 `@log` + `@measure("...")`，调用一次，观察日志顺序：先 log 进 → measure 进 → 原方法 → measure 出 → log 出（验证"从下往上应用"）
5. 用 `@memo` 装饰一个纯函数方法（如 `fib(n)` 或 `square(x)`），连续两次调用相同参数，验证方法体**只执行了一次**（方法体里打印一行"计算中"即可观察）

### 技术要点
- 方法装饰器签名：`(originalMethod, context)` → 返回替换方法（README「原理」的签名）
- 裸装饰器（`@log`）vs 工厂（`@measure("label")`）：需要配置参数时多包一层函数
- 叠加顺序：**从下往上应用**——先应用的包在内层（README「核心概念 3」）
- `this` 绑定：包装函数里必须 `originalMethod.apply(this, args)`（或 `.call(this, ...args)`），否则方法内访问 `this` 字段会炸
- `@memo` 的缓存 Map 放进工厂闭包：在返回装饰器之前 `const cache = new Map()`，用参数串做 key

### 超纲提示
🔧 `context` 里不止有 `name`：`context.kind`（"method" / "class" / "field" ...）、`context.static`、`context.private`——`console.log(context)` 看看它到底长什么样。

### 自测方法
```bash
cd s32_typescript && npx tsc -p s13_decorator && node s13_decorator/dist/practice_log.js
# 前提：include 已包含 practice_log.ts（见上方「编译练习文件」做法 A；不想改 tsconfig 就换做法 B）
# 观察：① 叠加装饰器时 进/出 日志的先后顺序（应为 log 进 → measure 进 → 原方法 → measure 出 → log 出）
#       ② @memo 第二次调用相同参数时没有"计算中"输出
```

## 需求 2：@route 路由注册——迷你框架（⭐⭐ 组合 | 核心技能：类装饰器 + 方法装饰器收集元数据）
- [ ] 完成

### 背景
NestJS 的 `@Controller` / `@Get`、MCP server 的 `@tool("name")`——声明式框架的骨架全是"装饰器收集元数据 + 运行时查表分发"。亲手写一个迷你版，框架的神秘感就没了。

### 要做什么（验收标准）
1. `@Controller(prefix)` 类装饰器：登记这个类（prefix 如 `"/users"`）
2. `@route(method, path)` 方法装饰器：把 method + path 收集进**类的路由表**
3. `Router` 类：
   - `addController(cls)`：汇总一个类的路由表（prefix 与 path 拼接成完整路径）
   - `handle(req)`：分发——`req = { method, path }`，匹配到则调用对应方法，返回 `{ status: 200, body }`；没匹配到返回 `{ status: 404, body: {...} }`（先不做真 HTTP）
4. 写两个 controller（如 UsersController、PostsController）各带 2 个路由，演示：注册后打印路由表 + 分发几个请求看结果

### 技术要点
- 类装饰器拿到的是 constructor，装饰器函数在**类定义时**执行一次
- 元数据存哪？两个候选：**类的静态属性**（给 constructor 挂 `cls.routes = []`）或模块级 `Map<constructor, 路由表>`
- 装饰器求值顺序：**方法装饰器先于类装饰器执行**！所以类装饰器执行时，方法已经把自己的路由记好了——整个模式成立的前提
- 方法装饰器里用 `context.name` 作为路由对应的处理函数名（`instance[handlerName](req)` 调用）
- 路由表结构自己定：`{ method, path, handlerName }` 起步，够用即可；路径匹配从精确相等开始，`:id` 通配是超纲

### 超纲提示
🔧 把 `handle(req)` 接到 s16 的 `createServer` 上：`req` 换成真实的 `IncomingMessage`，返回的 `{status, body}` 直接 `res.writeHead + res.end`——一个可 curl 的声明式 API 框架就诞生了（学完 s16 回来做这步）。

### 自测方法
```bash
cd s32_typescript && npx tsc -p s13_decorator && node s13_decorator/dist/practice_router.js
# 验收点：路由表打印完整（prefix 已拼接）；handle({method:"GET", path:"/users"}) → 200 + 对应 body；
#        不存在的路径 → 404
```

## 需求 3：简易 DI 容器（⭐⭐⭐ 挑战 | 核心技能：字段装饰器 + 依赖注入容器雏形）
- [ ] 完成

### 背景
NestJS 的 `@Injectable` + `@Inject` 就是这题的工程版。核心只有两步：**用元数据记录"这个字段要什么"**，**容器在实例化时查表把依赖塞进去**。理解了骨架，框架的魔法就只剩工作量了。

### 要做什么（验收标准）
1. `@injectable()` 类装饰器：标记这个类可以被容器管理
2. `@inject(token)` 字段装饰器：标记"这个字段要注入什么"。注意字段装饰器签名是 `(undefined, context)`——拿不到值，只能**记录元数据**（提示：挂到类的静态属性，或用模块级 WeakMap 记录"这个类的这个字段要注入什么 token"）
3. `Container` 类：
   - `register(token, instance)`：注册一个已存在的实例（比如 Database）
   - `resolve(cls)`：`new cls()` 之后，遍历标了 `@inject` 的字段，从容器里取对应实例赋值
4. 演示三层装配：`Database`（先 register 实例）→ `UserService`（`@inject` 拿 Database）→ `UserController`（`@inject` 拿 UserService）；`resolve(UserController)` 后调用方法能正常工作，打印每一层的装配结果

### 技术要点
- 字段装饰器签名：`(undefined, context)`，`context.name` 就是字段名
- 装饰器求值顺序：**字段装饰器先于类装饰器执行**——类装饰器执行时所有字段的注入标记已记录完毕
- 元数据记录三选一：类静态属性 / 模块级 Map / WeakMap（key 用 constructor，不泄漏）
- 容器装配逻辑 = 查元数据表 → `new cls()` → 按记录逐字段赋值；循环依赖先不管（超纲）
- 泛型签名 `resolve<T>(cls: new (...args: never[]) => T): T` 让返回值带类型

### 超纲提示
🔧 `reflect-metadata` 包（`npm i reflect-metadata`）：用 `Reflect.metadata("design:type", ...)` 让编译器自动反射字段的真实类型，`@inject()` 不带 token 也能靠反射找到依赖类型——NestJS 早期版本就是这么做的。

### 自测方法
```bash
cd s32_typescript && npx tsc -p s13_decorator && node s13_decorator/dist/practice_di.js
# 验收点：resolve 出的 UserController 能一路调到 Database 的方法；打印三层字段值证明注入成功
```

## 做完之后
- 自查：你用了本章哪些概念？——方法装饰器 / 类装饰器 / 字段装饰器、装饰器工厂、叠加顺序（从下往上）、装饰器求值顺序（字段 → 方法 → 类）、不可擦除语法与编译流程（`__esDecorate`）
- 想继续深挖：回看本章 README 的「跟 Agent 的关系」，选一个点展开——比如把需求 2 的 Router 升级成 MCP 的 `@tool` 模式，或用 DI 容器给你的 mini Agent 组装工具
