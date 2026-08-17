/**
 * s32-05 辅助模块：一个「老式」的 CommonJS 模块（纯 JS，无类型）
 *
 * .cjs 扩展名 = 无论 package.json 写什么，都按 CommonJS 解析。
 * ESM 想用它，只能通过 createRequire 或默认互操作。
 */

const version = "1.0.0";

function legacyGreet(name) {
  return `【CJS】你好，${name}！(版本 ${version})`;
}

module.exports = { version, legacyGreet };
