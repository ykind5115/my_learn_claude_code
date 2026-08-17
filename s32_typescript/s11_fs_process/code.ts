/**
 * s32-11: 文件系统 / subprocess — Agent 工具的文件层
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - fs/promises 和旧式 callback API 有什么区别？该用哪个？
 *   - 路径拼接为什么必须用 path.join 而不是字符串 +？
 *   - 读大文件为什么用流而不是 readFile？
 *   - exec / spawn / spawnSync 各适合什么场景？命令注入怎么防？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     node s32_typescript/s11_fs_process/code.ts
 *     （演示文件都在 s11_fs_process/.demo/ 里，跑完自动清理）
 */

import { mkdir, writeFile, readFile, appendFile, readdir, rm, rename } from "node:fs/promises";
import { createReadStream } from "node:fs";
import { join, basename } from "node:path";
import { spawnSync } from "node:child_process";
import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";

// 演示工作区：永远基于 import.meta.dirname 定位（不依赖 cwd！）
const workspace = join(import.meta.dirname, ".demo");

async function demo_all(): Promise<void> {
  print_section("s32-11: 文件系统 / subprocess");

  // ═══════════════════════════════════════════════════════════
  // 第 1 步: fs/promises 基础读写
  // ═══════════════════════════════════════════════════════════
  print_step(1, "fs/promises — 异步文件读写");

  await rm(workspace, { recursive: true, force: true });   // 清理上次演示残留
  await mkdir(join(workspace, "notes"), { recursive: true });

  const notePath = join(workspace, "notes", "todo.md");
  await writeFile(notePath, "# 今日待办\n- 学 TypeScript\n", "utf8");
  console.log(`  已写入: ${notePath}`);

  const content = await readFile(notePath, "utf8");
  console.log(`  读回内容: ${JSON.stringify(content)}`);

  await appendFile(notePath, "- 写文件系统 demo\n", "utf8");
  console.log(`  追加后: ${JSON.stringify(await readFile(notePath, "utf8"))}`);
  print_note("fs/promises 返回 Promise，配合 await 就是干净的直线代码。");
  print_note("老式 fs.readFile(path, cb) 是 error-first callback（s10 提过）——新代码用 promises 版。");

  // ═══════════════════════════════════════════════════════════
  // 第 2 步: path — 路径处理
  // ═══════════════════════════════════════════════════════════
  print_step(2, "path.join — 永远别用字符串拼路径");

  const joined = join("a", "b", "..", "c.txt");
  console.log(`  join("a", "b", "..", "c.txt") = ${joined}（自动处理 .. 和平台分隔符）`);
  console.log(`  basename(joined) = ${basename(joined)}`);
  console.log(`  import.meta.dirname = ${import.meta.dirname}（本文件的目录，不随 cwd 变）`);
  print_key_point("Windows 用 \\、Linux 用 /，字符串拼接跨平台必炸。\n    路径一律 path.join + import.meta.dirname——这是本模块的铁律。");

  // ═══════════════════════════════════════════════════════════
  // 第 3 步: 目录遍历 + 改名
  // ═══════════════════════════════════════════════════════════
  print_step(3, "目录遍历 / 改名 — readdir 与 rename");

  await writeFile(join(workspace, "notes", "idea.md"), "# 灵感\n- 做一个 CLI\n", "utf8");
  await writeFile(join(workspace, "notes", "draft.txt"), "草稿", "utf8");

  const entries = await readdir(join(workspace, "notes"), { withFileTypes: true });
  const mdFiles = entries.filter((e) => e.isFile() && e.name.endsWith(".md"));
  console.log(`  notes/ 下的 .md 文件: ${mdFiles.map((e) => e.name).join(", ")}`);

  await rename(join(workspace, "notes", "draft.txt"), join(workspace, "notes", "draft.md"));
  console.log(`  改名后: ${(await readdir(join(workspace, "notes"))).join(", ")}`);
  print_note("withFileTypes 直接给出文件类型，不用再逐个 stat。");

  // ═══════════════════════════════════════════════════════════
  // 第 4 步: 流式读 vs 一次性读
  // ═══════════════════════════════════════════════════════════
  print_step(4, "流 vs 一次性读 — 大文件的分块哲学");

  // 生成一个约 1MB 的文件
  const bigPath = join(workspace, "big.txt");
  const oneKb = "x".repeat(1024);
  await writeFile(bigPath, oneKb.repeat(1024), "utf8");

  // 方式 A：一次性读 —— 整个文件进内存
  const t1 = performance.now();
  const whole = await readFile(bigPath, "utf8");
  const ms1 = Math.round(performance.now() - t1);
  console.log(`  一次性 readFile: ${(whole.length / 1024).toFixed(0)}KB 全部进内存, ${ms1}ms`);

  // 方式 B：流式读 —— 一块一块处理
  const t2 = performance.now();
  let chunkCount = 0;
  let totalBytes = 0;
  const stream = createReadStream(bigPath, { encoding: "utf8", highWaterMark: 64 * 1024 });
  for await (const chunk of stream) {
    chunkCount += 1;
    totalBytes += chunk.length;
  }
  const ms2 = Math.round(performance.now() - t2);
  console.log(`  流式读: ${chunkCount} 个块, 共 ${(totalBytes / 1024).toFixed(0)}KB, ${ms2}ms`);
  print_key_point("readFile 适合小文件；大文件/无限数据（日志、网络流）用流：\n    固定小块内存，边读边处理。for await...of 是流的异步迭代糖。");

  // ═══════════════════════════════════════════════════════════
  // 第 5 步: 子进程 — exec vs spawn
  // ═══════════════════════════════════════════════════════════
  print_step(5, "child_process — exec vs spawn vs spawnSync");

  console.log(`  ┌────────────┬──────────────────────────────────────┐`);
  console.log(`  │ spawnSync  │ 同步等待，适合演示和短命令              │`);
  console.log(`  │ exec       │ 缓冲全部输出，适合小输出（有注入风险）   │`);
  console.log(`  │ spawn      │ 流式输出，适合大输出/长任务（参数数组）  │`);
  console.log(`  └────────────┴──────────────────────────────────────┘`);

  const r1 = spawnSync(process.execPath, ["-e", "console.log('子进程: 1+1 =', 1+1)"], { encoding: "utf8" });
  console.log(`  spawnSync node -e → ${r1.stdout.trim()}`);

  const r2 = spawnSync(process.execPath, ["--version"], { encoding: "utf8" });
  console.log(`  spawnSync node --version → ${r2.stdout.trim()}`);

  const gitCheck = spawnSync("git", ["--version"], { encoding: "utf8", shell: process.platform === "win32" });
  if (gitCheck.status === 0) {
    console.log(`  git 可用: ${gitCheck.stdout.trim()}`);
    print_note("Agent 的 Bash 工具执行 git status / git diff 就是 spawn 这类调用。");
  } else {
    print_note("git 不可用，跳过（不影响本章主线）。");
  }
  print_key_point("防命令注入的金标准：\n    ❌ exec(`git log ${userInput}`) —— 用户输入拼进字符串，可以执行任意命令\n    ✅ spawn('git', ['log', userInput]) —— 参数数组，输入永远只是「一个参数」");

  // ═══════════════════════════════════════════════════════════
  // 第 6 步: 清理
  // ═══════════════════════════════════════════════════════════
  print_step(6, "清理 — 演示完擦干净");

  await rm(workspace, { recursive: true, force: true });
  console.log(`  已删除 ${workspace}`);
  print_note("每次运行前清理 + 结束后清理——演示代码不污染工作区。");

  console.log();
  print_key_point("fs/promises、path.join、流、spawn——Agent 的 Read/Write/Bash 工具内核齐了。\n    下一章：高级类型——keyof、条件类型、infer 的进阶玩法。");
}

await demo_all();
