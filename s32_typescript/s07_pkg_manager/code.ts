/**
 * s32-07: npm / pnpm — 把别人的代码装进自己的项目
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - package.json 的关键字段各管什么？
 *   - semver 的 ^ 和 ~ 有什么区别？
 *   - npm 和 pnpm 的 node_modules 布局有什么本质不同？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     node s32_typescript/s07_pkg_manager/code.ts
 *     （依赖装没装都能跑——没装会给友好提示）
 */

import { createRequire } from "node:module";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { ChalkInstance } from "chalk";
import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";

// Windows 上 npm/pnpm 是 .cmd 垫片脚本；这里用 shell:true 交给系统解析。
// 注意：shell:true 拼接用户输入会有命令注入风险（s11 细讲），演示里参数全是常量，安全。
function runCommand(cmd: string, args: string[]): string {
  const r = spawnSync(cmd, args, {
    encoding: "utf8",
    cwd: moduleRoot,
    shell: process.platform === "win32",
  });
  if (r.error) return `执行失败: ${r.error.message}`;
  const out = r.stdout ?? "";
  const errOut = r.stderr ?? "";
  return out.trim() || errOut.trim();
}

// 模块根目录（package.json 所在处）
const moduleRoot = join(import.meta.dirname, "..");

// 动态加载 chalk：没装时给友好提示而不是崩溃
async function loadChalk(): Promise<ChalkInstance | null> {
  try {
    const mod = await import("chalk");
    return mod.default as ChalkInstance;
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === "ERR_MODULE_NOT_FOUND") {
      console.log(`  ${Color.WARNING}检测到 chalk 未安装。${Color.RESET}`);
      console.log(`  请先运行: cd s32_typescript && npm install`);
      return null;
    }
    throw e;
  }
}

async function demo_all(): Promise<void> {
  print_section("s32-07: npm / pnpm");

  // ═══════════════════════════════════════════════════════════
  // 第 1 步: package.json — 项目的身份证
  // ═══════════════════════════════════════════════════════════
  print_step(1, "package.json — 项目的身份证");

  const pkgPath = join(moduleRoot, "package.json");
  const pkg = JSON.parse(readFileSync(pkgPath, "utf8")) as {
    name: string;
    type: string;
    scripts: Record<string, string>;
    devDependencies: Record<string, string>;
    engines: Record<string, string>;
  };

  console.log(`  name          = ${pkg.name}`);
  console.log(`  type          = ${pkg.type}（决定模块系统，s05 讲过）`);
  console.log(`  engines       = node ${pkg.engines.node}（声明运行环境要求）`);
  console.log(`  scripts       = ${JSON.stringify(pkg.scripts, null, 2).replace(/\n/g, "\n                 ")}`);
  console.log(`  devDependencies = ${Object.keys(pkg.devDependencies).join(", ")}`);
  print_key_point("dependencies = 运行时需要的包；devDependencies = 只有开发时需要（typescript、@types/node 都是）。\n    scripts 里的 \"typecheck\" 就是本模块质检员的开关。");

  // ═══════════════════════════════════════════════════════════
  // 第 2 步: semver — 版本号的三段式
  // ═══════════════════════════════════════════════════════════
  print_step(2, "semver — 版本号的三段式与 ^ ~");

  console.log(`  版本号 = 主版本.次版本.补丁版本 (major.minor.patch)`);
  console.log(`  例: typescript 5.8.2 = 大版本 5 / 功能版本 8 / 修复版本 2`);
  console.log();
  console.log(`  ^5.4.0  →  5.x.x 任意版本（允许次版本和补丁更新）  ← 最常用`);
  console.log(`  ~1.2.3  →  1.2.x 任意版本（只允许补丁更新）`);
  console.log(`  1.2.3   →  精确锁定这一个版本`);
  console.log(`  *       →  任意版本（危险，别用）`);
  print_key_point("语义化版本约定：大版本变化 = 不兼容；次版本 = 新功能；补丁 = 修 bug。\n    ^ 是默认推荐——拿到新功能和 bug 修复，又不会被不兼容的大版本坑。");

  // ═══════════════════════════════════════════════════════════
  // 第 3 步: 使用真实依赖 chalk
  // ═══════════════════════════════════════════════════════════
  print_step(3, "装一个真实依赖 — chalk 彩色输出");

  const chalk = await loadChalk();
  if (chalk) {
    console.log(`  ${chalk.red("红")}${chalk.green("绿")}${chalk.blue("蓝")}${chalk.yellow("黄")} ${chalk.bold.cyan("加粗青")} —— chalk 在干活`);
    const require = createRequire(import.meta.url);
    const chalkEntry = require.resolve("chalk");
    console.log(`  chalk 的物理位置: ${chalkEntry}`);
    print_note("import 时 Node 从 node_modules 里按包名找——这就是「装包」的意义。");
    print_note("chalk v5 是 ESM-only：只有 ESM 项目能直接 import（本模块恰好是）。\n    老 CJS 项目只能用 v4——装包前看清包的模块系统，能少踩一半坑。");
  } else {
    print_note("（上面的提示就是「依赖缺失时的友好错误处理」——真实工程必备）");
  }

  // ═══════════════════════════════════════════════════════════
  // 第 4 步: 工具链检查 + scripts 实操
  // ═══════════════════════════════════════════════════════════
  print_step(4, "工具链检查 + scripts 实操");

  console.log(`  node  = ${runCommand("node", ["--version"])}`);
  const npmV = runCommand("npm", ["--version"]);
  console.log(`  npm   = ${npmV || "未安装"}`);
  const pnpmV = runCommand("pnpm", ["--version"]);
  console.log(`  pnpm  = ${pnpmV || "未安装"}`);

  // 实际跑一个 npm script（这就是 package.json scripts 的用法）
  print_note("跑一下本模块的 typecheck script（和你在终端敲 npm run typecheck 一样）...");
  const tcOut = runCommand("npm", ["run", "typecheck"]);
  console.log(`  typecheck 结果: ${tcOut.includes("error") ? Color.ERROR + "有错误" : Color.SUCCESS + "✅ 零错误" + Color.RESET}`);
  print_key_point("npm run <脚本名> = 执行 package.json scripts 里的命令。\n    团队协作时把常用命令写进 scripts，新成员 clone 下来照着跑就行。");

  // ═══════════════════════════════════════════════════════════
  // 第 5 步: npm vs pnpm — 两种装法
  // ═══════════════════════════════════════════════════════════
  print_step(5, "npm vs pnpm — 同样的包，不同的放法");

  console.log(`  npm   把依赖平铺复制到 node_modules/（每装一次复制一份）`);
  console.log(`  pnpm  全局仓库存一份 + node_modules 里放符号链接`);
  console.log();
  console.log(`  对比：`);
  console.log(`  ┌──────────┬──────────────┬─────────────────────┐`);
  console.log(`  │          │ 磁盘占用      │ 特性                 │`);
  console.log(`  ├──────────┼──────────────┼─────────────────────┤`);
  console.log(`  │ npm      │ 每个项目一份  │ 平铺，可能有幻影依赖  │`);
  console.log(`  │ pnpm     │ 全局只存一份  │ 符号链接，隔离严格     │`);
  console.log(`  │ yarn     │ 类似 npm     │ 中间态，用得少        │`);
  console.log(`  └──────────┴──────────────┴─────────────────────┘`);
  print_note("幻影依赖：npm 平铺后你能 import 到没写在 package.json 里的包，\n    pnpm 的严格布局让你只能用声明过的依赖——更不容易埋雷。");
  print_note("lock 文件（package-lock.json / pnpm-lock.yaml）锁住精确版本，\n    保证所有人和 CI 装出来一模一样——必须提交进 git。");
  print_key_point("警告：同一项目别 npm/pnpm 来回 install——两种 node_modules 布局会互相污染。\n    选一个用到底（本模块默认 npm）。");

  console.log();
  print_key_point("package.json、semver、装包、scripts、npm vs pnpm——工程化入门了。\n    下一章：泛型——让类型也能当参数。");
}

await demo_all();
