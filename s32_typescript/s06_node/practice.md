# s32-06: Node.js — 动手需求

[← 返回总索引](../PRACTICE.md) | [本章教程](./README.md)

> 一句话本章核心思想：**Node = V8（执行 JS）+ libuv（异步 I/O 引擎），TypeScript 代码最终都跑在这两个底座上。**

学完本章，用下面这些需求把知识变成肌肉记忆。**只给需求和提示，不给完整代码**——卡住了回到主项目提问。

## 使用说明
- 前置技能：s01~s06（s04 的 async 用于读流式 body，s05 的模块化会用到）
- 自测方式：`node s32_typescript/s06_node/<文件名>.ts` 直跑；服务类需求用脚本内 `fetch` 自测，也可另开终端 `curl`；`cd s32_typescript && npm run typecheck` 零报错
- 解答文件建议放本章目录内，命名 `practice_<名字>.ts`

## 需求 1：环境变量配置检查器（⭐ 入门 | 核心技能：process.env / process.argv / exitCode）
- [ ] 完成

### 背景
README 说密钥住进 `process.env`，那么服务启动前"检查配置齐不齐"就是第一道门：缺了什么配置，启动时就该明确说不，而不是跑起来才炸。这个十几行的小工具，是每个真实服务都有的启动守卫的雏形。

### 要做什么（验收标准）
1. `check-env.ts`：定义必需变量列表 `["PORT", "DB_URL", "SECRET_KEY"]`
2. 逐个检查 `process.env`：
   - 有缺失 → 打印 `[MISSING] PORT` 这样的清单，**以 `process.exitCode = 1` 退出**（非零退出码 = 告诉调用方"失败了"）
   - 全部齐全 → 打印 `✅ 配置齐全`，exitCode 保持 0
3. 支持 `--verbose` 参数（用 `process.argv` 判断）：多打印"环境变量总数 = N"和每个必需变量的状态
4. 测试时用**占位值**模拟（`$env:PORT="8080"` 这种），绝不放真实密钥；脚本只检查"是否存在"，**永不打印 SECRET_KEY 的值**（README 的环境变量安全红线）
5. typecheck 零报错

### 技术要点
- **process.env 读法**：`process.env.PORT`，没设置就是 `undefined`——用 `=== undefined` 判断，别用 falsy（空字符串也算"设了"）
- **process.argv 解析 flag**：`process.argv.slice(2)` 拿用户参数，遍历找 `--verbose`（README 第 1 点）
- **process.exitCode vs process.exit**：设置 `exitCode` 让代码自然跑完再以该码退出；`process.exit()` 会立刻掐断，还可能丢掉没写完的异步输出——启动守卫用 exitCode 更稳（README 第 1 点）
- **模板字符串输出**：`[MISSING] ${name}` 这种反引号写法

### 超纲提示
🔧 `dotenv` 库（s07 学完装包后可用）——`.env` 文件 → `process.env` 的标准路径，README 说这就是 Agent 拿 API Key 的链路。装上后放一个 `.env` 在项目根，让脚本自动读它。

### 自测方法
```bash
# PowerShell：先故意缺变量
node s32_typescript/s06_node/check-env.ts
echo "退出码 = $LASTEXITCODE"          # 应看到 1
# 补全后再跑（占位值，别用真密钥）
$env:PORT="8080"; $env:DB_URL="postgres://localhost/db"; $env:SECRET_KEY="dev-only"
node s32_typescript/s06_node/check-env.ts
echo "退出码 = $LASTEXITCODE"          # 应看到 0
node s32_typescript/s06_node/check-env.ts --verbose   # 多打印环境变量总数
cd s32_typescript && npm run typecheck
# bash 对应：env -u PORT node s32_typescript/s06_node/check-env.ts  /  export PORT=8080 ...
```

## 需求 2：迷你 JSON API（⭐⭐ 组合 | 核心技能：createServer + JSON + 读请求体 for await）
- [ ] 完成

### 背景
s16 的 HTTP API 是综合实战，但它的内核就这几十行：createServer + 路由分发 + JSON 读写。把最小内核跑熟，后面所有 HTTP 相关章节都是在这上面加东西。这一题也是"端口 0 随机 + fetch 自测"这套演示姿势的第一次实战。

### 要做什么（验收标准）
1. `practice_api.ts`：`createServer` 处理以下路由——
   - `GET /health` → `{ ok: true }`
   - `GET /time` → `{ iso: "<当前 ISO 时间>" }`
   - `GET /echo?msg=hi` → `{ msg: "hi" }`（用 `new URL(req.url, "http://x")` 解析 query）
   - `POST /echo` → 读 JSON body（`for await` 拼流），原样返回 `{ ...body }`
   - 其他路径 → 404 + `{ error: "not found" }`
2. 响应统一 `Content-Type: application/json; charset=utf-8`，用 `JSON.stringify` 序列化
3. `listen(0)` 随机端口，打印实际端口（从 `server.address()` 取）
4. 脚本内用 node 内置 `fetch` 依次打四个端点，全部断言通过后 `server.close()` 收尾（不留悬挂进程）
5. typecheck 零报错

### 技术要点
- **new URL(req.url, base) 解析**：`req.url` 是路径 + 查询串，套上 base 才能拿 `.searchParams`（README 内置模块表的 node:url）
- **for await 读流式 body**：`for await (const chunk of req)` 把 Buffer 块拼成字符串——s04 的异步节奏在 http 上的应用
- **JSON.stringify + Content-Type 头**：`res.setHeader` + `res.end(JSON.stringify(...))`（README 最小服务器三件套）
- **listen(0) 随机端口 + close 收尾**：演示代码不打架、不留进程（README 核心概念 4）
- POST 的 body 不是合法 JSON 时要兜住：try/catch 回 400

### 超纲提示
🔧 `URLSearchParams` 单独拿出来用：`new URLSearchParams(req.url.split("?")[1])` 直接解析 query——和 `new URL` 的结果互通，二选一即可。

### 自测方法
```bash
node s32_typescript/s06_node/practice_api.ts
# 脚本内 fetch 四个端点全部 ✅ 后自动 close 退出

# 想用 curl 另开终端测：给脚本加一个 --stay 参数（不 close、挂起进程），然后：
curl http://127.0.0.1:<端口>/health
curl "http://127.0.0.1:<端口>/echo?msg=hi"
curl -X POST -H "Content-Type: application/json" -d '{"a":1}' http://127.0.0.1:<端口>/echo
cd s32_typescript && npm run typecheck
```

## 需求 3：静态文件服务器（⭐⭐⭐ 挑战 | 核心技能：http + path + fs（前瞻 s11）+ 路径安全）
- [ ] 完成

### 背景
把服务器和文件系统连起来，是理解"路径拼接为什么危险"的最好教材：`/../package.json` 这类路径一旦被天真地拼进文件路径，你的服务器就把仓库根目录的内容全暴露了。写出"能拦穿越"的服务器，你对路径安全的认识就到位了——这是安全红线，必须亲眼看到它被拦下。

### 要做什么（验收标准）
1. 本章目录下建 `public/`，放 `index.html` 和 `a.txt` 各一个
2. `practice_static.ts`：`createServer` + `node:path` + `node:fs/promises`（fs 是 s11 的前瞻，先照猫画虎用起来）——
   - `GET /` → 返回 `public/index.html`；`GET /a.txt` → 返回内容
   - `Content-Type` 按扩展名粗判：`.html` → `text/html; charset=utf-8`，`.txt` → `text/plain; charset=utf-8`，其他 → `application/octet-stream`
   - 文件不存在 → 404 + 简单文本
3. **路径安全红线**：把请求路径转成绝对路径后，必须做 `startsWith(publicRoot)` 检查；访问 `/../package.json`、`/..%2f..` 一律 403 拒绝，**绝不返回任何文件内容**
4. typecheck 零报错

### 技术要点
- **path.join + 规范化 + startsWith 检查**：`path.join(publicRoot, decodeURIComponent(pathname))` 得到目标路径，再判断它是否仍在 publicRoot 之下——`..` 会被 join 吃掉，但正是因此才必须检查越界
- **readFile 错误 → 404**：`fs.readFile` 失败（ENOENT）时回 404，而不是让进程崩溃——错误分支是 HTTP 服务的基本功
- **import.meta.dirname 定位 public**：`path.join(import.meta.dirname, "public")`——绝不依赖 `process.cwd()`（项目约定）
- **decodeURIComponent**：URL 里的 `%2e%2e` 是 `..` 的编码形态，不解码就比对不了真实路径（超纲点展开）
- 静态文件路径是**输入**，输入必须校验——和 s03 的 narrowing 精神一致：先收窄再使用

### 超纲提示
🔧 `decodeURIComponent` 处理编码穿越：请求路径先 `decodeURIComponent` 再进 `path.join`，这样 `%2e%2e` 会被还原成 `..` 并被你的越界检查拦下；别忘了 decode 也可能抛错（非法编码），try/catch 住。

### 自测方法
```bash
node s32_typescript/s06_node/practice_static.ts
# 脚本内 fetch 断言：/ → index.html 内容、/a.txt → 内容、/../package.json → 403/404 且 body 不含文件内容
# 另开终端手动试：
curl http://127.0.0.1:<端口>/
curl http://127.0.0.1:<端口>/a.txt
curl --path-as-is http://127.0.0.1:<端口>/../package.json            # 必须被拦
curl --path-as-is "http://127.0.0.1:<端口>/..%2f..%2fpackage.json"   # 必须被拦
cd s32_typescript && npm run typecheck
# 红线验证：任何穿越请求的响应里都绝不能出现 package.json 的内容
```

## 做完之后
- 自查：你用了本章哪些概念？——process.env / process.argv / exitCode、createServer + listen(0) + close、new URL 解析、for await 流式读取、Content-Type、path.join 路径安全、import.meta.dirname
- 想继续深挖：回看本章 README 的"跟 Agent 的关系"，选一个点展开——比如把需求 2 的 API 和需求 3 的静态服务器合并：一个服务器同时服务 JSON 路由和静态文件，这正是 Agent 本地工具服务的常见形态
