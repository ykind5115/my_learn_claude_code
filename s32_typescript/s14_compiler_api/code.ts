/**
 * s32-14: TypeScript Compiler API — 用 TypeScript 解析 TypeScript
 *
 * ═══════════════════════════════════════════════════════════════
 * 学完本章你应该能回答：
 *   - tsc 背后的库是什么？怎么用它解析代码？
 *   - AST 是什么？怎么遍历它？
 *   - 怎么用 Compiler API 写一个「代码分析小工具」？
 * ═══════════════════════════════════════════════════════════════
 *
 * 启动方式:
 *     cd s32_typescript && npm install（需要 typescript 包）
 *     node s32_typescript/s14_compiler_api/code.ts
 */

import ts from "typescript";
import { Color, print_step, print_note, print_key_point, print_section } from "../utils.ts";

// 一段「待分析」的源码（字符串里的代码）
const sampleCode = `
interface User {
  name: string;
  age: number;
}

function greet(user: User, times: number = 1): string {
  return \`你好，\${user.name}！\`.repeat(times);
}

export function sum(...nums: number[]): number {
  return nums.reduce((a, b) => a + b, 0);
}

export const PI = 3.14159;
`;

function demo_all(): void {
  print_section("s32-14: TypeScript Compiler API");

  // ═══════════════════════════════════════════════════════════
  // 第 1 步: 把源码字符串解析成 AST
  // ═══════════════════════════════════════════════════════════
  print_step(1, "createSourceFile — 源码字符串 → 语法树");

  const sourceFile = ts.createSourceFile(
    "demo.ts",                  // 虚拟文件名（用于报错定位）
    sampleCode,                 // 源码
    ts.ScriptTarget.Latest,     // 语法版本
    true,                       // setParentNodes
  );

  console.log(`  解析成功，kind = ${ts.SyntaxKind[sourceFile.kind]}`);
  print_note("AST（抽象语法树）= 代码的树形结构：每个节点代表一个语法单元。");
  print_note("编辑器的高亮、跳转、重构、ESLint 规则、格式化——全部建立在 AST 上。");

  // ═══════════════════════════════════════════════════════════
  // 第 2 步: 递归遍历 AST
  // ═══════════════════════════════════════════════════════════
  print_step(2, "遍历 AST — 缩进打印语法树");

  const lines: string[] = [];
  const walk = (node: ts.Node, indent: number): void => {
    lines.push("  ".repeat(indent) + ts.SyntaxKind[node.kind]);
    ts.forEachChild(node, (child) => walk(child, indent + 1));
  };
  walk(sourceFile, 0);
  // 只展示前 14 行（树很大，全打印刷屏）
  console.log(lines.slice(0, 14).join("\n"));
  print_note(`（完整树有 ${lines.length} 个节点，这里截取开头）`);
  print_key_point("forEachChild 递归 + SyntaxKind 对照表 = AST 遍历的全部。\n    ts.SyntaxKind 是库里的编译产物 enum——s01 说的「库里的 enum 随便用」。");

  // ═══════════════════════════════════════════════════════════
  // 第 3 步: 提取函数签名 — 写一个分析小工具
  // ═══════════════════════════════════════════════════════════
  print_step(3, "提取函数签名 — 一个 10 行的分析工具");

  const signatures: string[] = [];
  const collect = (node: ts.Node): void => {
    if (ts.isFunctionDeclaration(node)) {
      signatures.push(node.getText(sourceFile));
    }
    ts.forEachChild(node, collect);
  };
  collect(sourceFile);

  console.log(`  从源码里挖出的函数签名：`);
  for (const sig of signatures) {
    console.log(`    ${Color.HIGHLIGHT}${sig}${Color.RESET}`);
  }
  print_note("ts.isFunctionDeclaration(node) 是类型守卫（s03！）——收窄后 node.name 可用。");
  print_key_point("「遍历 AST + 过滤节点类型 + 提取信息」三步曲，\n    就是 ESLint 规则、自动文档生成器、代码统计工具的骨架。");

  // ═══════════════════════════════════════════════════════════
  // 第 4 步: transpileModule — 亲眼看到类型擦除
  // ═══════════════════════════════════════════════════════════
  print_step(4, "transpileModule — 亲眼看到「撕标签」");

  const js = ts.transpileModule(sampleCode, {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.ESNext,
    },
  });

  console.log(`  编译产物（interface 消失，类型标注全被擦除）：`);
  console.log(`  ${Color.DIM}${"-".repeat(50)}${Color.RESET}`);
  for (const line of js.outputText.trim().split("\n")) {
    console.log(`  ${Color.DIM}${line}${Color.RESET}`);
  }
  console.log(`  ${Color.DIM}${"-".repeat(50)}${Color.RESET}`);
  print_key_point("interface User 没了、类型标注没了、只剩纯 JS——\n    s00 说的「类型擦除」在这里看到了机器实现。\n    Node 直跑 .ts 的 type stripping 做的也是同一件事。");

  // ═══════════════════════════════════════════════════════════
  // 第 5 步: 生态地图
  // ═══════════════════════════════════════════════════════════
  print_step(5, "生态地图 — 谁在用 Compiler API");

  console.log(`  ESLint 的 TS 规则     —— 遍历 AST 找问题模式`);
  console.log(`  Prettier             —— 解析 → 重排 → 打印`);
  console.log(`  VSCode 的 TS 服务    —— 实时 AST + 类型信息（跳转/重构/补全）`);
  console.log(`  代码生成器（OpenAPI → 类型）—— 读 schema 写 AST 再打印`);
  print_note("Claude Code 和编辑器工具链的语言分析层，底层都是这套 API。");

  console.log();
  print_key_point("createSourceFile → 遍历 AST → 提取信息 → transpileModule 擦除。\n    现在你既是 TS 的使用者，也是 TS 工具的制造者。\n    下一章：类型体操——类型系统的极限玩法。");
}

demo_all();
