/**
 * s16 实战：errors.ts — HTTP 错误与响应映射
 *
 * 知识点对照：
 *   - 自定义错误类（s10）：继承 Error + 修正 name + 附加上下文（statusCode）
 */

export class HttpError extends Error {
  readonly statusCode: number;

  constructor(statusCode: number, message: string) {
    super(message);
    this.name = "HttpError";
    this.statusCode = statusCode;
  }
}

/** 快捷构造：404 */
export function notFound(what: string): HttpError {
  return new HttpError(404, `${what} 不存在`);
}

/** 快捷构造：400 */
export function badRequest(message: string): HttpError {
  return new HttpError(400, message);
}
