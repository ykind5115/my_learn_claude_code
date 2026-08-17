/**
 * s32-05 辅助模块 B：
 *   - 默认导出（defaultGreet）—— 每个模块最多一个
 *   - let 导出（bValue）—— 演示 live binding
 *   - 与 lib-a 循环依赖
 */

import { aValue } from "./lib-a.ts";

// let 导出：导入方拿到的永远是「当前值」（活绑定）
export let bValue = "初始 B";

export function updateBValue(v: string): void {
  bValue = v;
}

// 这里引用了 lib-a 的 aValue —— 但只在函数被调用时读取，
// 那时 lib-a 早就初始化完了，所以循环依赖不会炸
export function getB(): string {
  return `bValue=${bValue}, 来自 lib-a 的 aValue=${aValue}`;
}

// 默认导出：import defaultGreet from "./lib-b.ts"
export default function defaultGreet(name: string): string {
  return `【默认导出】早上好，${name}！`;
}
