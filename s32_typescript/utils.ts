/**
 * s32_typescript 公共工具模块
 * 移植自 s31_system_design/utils.py
 *
 * 注意：
 * - Windows 旧版 cmd 不支持 ANSI 颜色，推荐用 Windows Terminal
 *   或 VS Code 内置终端运行（无颜色也不影响功能）。
 * - 各章节导入方式：import { Color, print_step } from "../utils.ts"
 *   （Node ESM + type stripping 要求相对导入必须带 .ts 扩展名）
 */

/** ANSI 颜色常量（对应 Python 版 Color 类的 13 个颜色） */
export const Color = {
  RESET: "\x1b[0m",
  BOLD: "\x1b[1m",
  DIM: "\x1b[2m",
  RED: "\x1b[31m",
  GREEN: "\x1b[32m",
  YELLOW: "\x1b[33m",
  BLUE: "\x1b[34m",
  MAGENTA: "\x1b[35m",
  CYAN: "\x1b[36m",
  HEADER: "\x1b[1m\x1b[36m",
  SUCCESS: "\x1b[32m",
  WARNING: "\x1b[33m",
  ERROR: "\x1b[31m",
  HIGHLIGHT: "\x1b[1m\x1b[35m",
} as const;

/** 分步标题: -- Step N: title -- */
export function print_step(num: number, title: string): void {
  console.log(`\n${Color.HEADER}-- Step ${num}: ${title} --${Color.RESET}`);
}

/** 注释行: -> text */
export function print_note(text: string): void {
  console.log(`  ${Color.YELLOW}-> ${text}${Color.RESET}`);
}

/** 金句: * text */
export function print_key_point(text: string): void {
  console.log(`  ${Color.HIGHLIGHT}* ${text}${Color.RESET}`);
}

/** 大标题: 60 个 '=' 上下夹住 */
export function print_section(title: string): void {
  const line = "=".repeat(60);
  console.log(`\n${Color.BOLD}${line}${Color.RESET}`);
  console.log(`${Color.HEADER}${title}${Color.RESET}`);
  console.log(`${Color.BOLD}${line}${Color.RESET}\n`);
}

/** 键值对: label: value */
export function print_metric(label: string, value: unknown): void {
  console.log(`  ${Color.BOLD}${label}:${Color.RESET} ${value}`);
}


