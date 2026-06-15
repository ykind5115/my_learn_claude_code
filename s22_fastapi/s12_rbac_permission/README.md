# s12: JWT 认证 — 登录拿 token，访问带 token

s01 → ... → s11 → `s12` → [s13](../s13_background_tasks/) → ... → s17
> *"JWT 就是一张带签名的身份证 — 服务器签发的，谁都不能伪造。登录后拿到它，后续请求带上它。"*
>
> **前提知识**: s11（理解中间件和异常处理）。s08（理解 Depends）。

---

## 1. 问题：怎么知道请求来自谁？

HTTP 是无状态的 — 每个请求都是独立的。上次请求你登录了，这次请求服务器怎么知道还是你？

方案：**登录时服务器发给你一个 Token（令牌），后续每个请求都带上它。**

---

## 2. JWT 是什么？

JWT = JSON Web Token。它由三部分组成，用 `.` 连接：

```
eyJhbGciOi...  .  eyJzdWIiOi...  .  SflKxwRJ...
     ↑                ↑               ↑
   Header          Payload         Signature
```

- **Header**（头部）：`{"alg": "HS256"}` — 用什么算法签名
- **Payload**（载荷）：`{"sub": "user_1", "exp": 1734567890}` — 存用户 ID 和过期时间
- **Signature**（签名）：用密钥对前两部分计算哈希 — 防篡改

> **核心原理**：任何人改了 Payload，签名就对不上了 → 服务器知道被篡改。
> 但任何人都**可以看到** Payload 的内容（它是 Base64 编码，不是加密）。所以**不要往 JWT 里放密码！**

---

## 3. 完整的认证流程

```
第 1 步: 注册
  POST /auth/register  {username, password}
  → 密码加盐哈希 → 存入数据库

第 2 步: 登录
  POST /auth/login  {username, password}
  → 验证密码 → 生成 JWT → 返回给客户端

第 3 步: 访问受保护的接口
  GET /me  (Header: Authorization: Bearer <token>)
  → FastAPI 提取 token → 验证签名 → 解析用户 → 返回数据

第 4 步: Token 过期后刷新（可选）
  POST /auth/refresh  {refresh_token}
  → 返回新的 access_token
```

---

## 4. 密码哈希 — 为什么不能存明文？

如果数据库被泄露，明文密码全部暴露。**哈希 + 加盐** 让密码不可逆：

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

# 注册时
hashed = pwd_context.hash("mypassword")
# → '$2b$12$...' （存储这个哈希值）

# 登录时验证
pwd_context.verify("mypassword", hashed)   # → True
pwd_context.verify("wrongpassword", hashed) # → False
```

---

## 5. FastAPI 的 OAuth2 支持

FastAPI 内置了 OAuth2 密码流：

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
# tokenUrl 告诉 Swagger UI "去哪个接口登录"

def get_current_user(token: str = Depends(oauth2_scheme)):
    # oauth2_scheme 自动从 Authorization: Bearer xxx 中提取 token
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("sub")
    ...
```

在 `/docs` 里，右上角会出现一个 **🔓 Authorize** 按钮。点了之后可以输入 token，Swagger UI 会自动在后续请求中带上它。

---

## 6. 关键：Access Token vs Refresh Token

| | Access Token | Refresh Token |
|---|---|---|
| 有效期 | 短（15分钟） | 长（7天） |
| 什么时候用 | 每次请求都带 | 只在刷新时用 |
| 泄露后果 | 15分钟后失效 | 可以换新 Access Token |

---

## 7. 常见错误

### ❌ 把密码明文存数据库

```python
user.password = "mypassword"  # ❌
user.hashed_password = pwd_context.hash("mypassword")  # ✅
```

### ❌ 往 JWT payload 里放敏感信息

```python
# ❌ JWT 的 Payload 只是 Base64 编码，不是加密！任何人都能解码
payload = {"password": user.password}

# ✅ 只放用户 ID 和必要信息
payload = {"sub": str(user.id), "username": user.username}
```

### ❌ 用弱密钥

```python
SECRET_KEY = "secret"  # ❌
SECRET_KEY = os.getenv("SECRET_KEY")  # ✅ 生产环境必须用环境变量
```

---

## 8. 自己动手

1. 用 `python-jose` 生成一个 JWT，然后去 [jwt.io](https://jwt.io) 粘贴看看里面的内容
2. 用 `passlib` 的 `hash()` 和 `verify()` 体验密码哈希
3. 实现注册 → 登录 → 访问 `/me` 的完整流程
