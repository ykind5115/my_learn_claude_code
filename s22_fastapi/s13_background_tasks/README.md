# s13: 权限控制 — 认证知道你是谁，授权知道你能做什么

s01 → ... → s12 → `s13` → [s14](../s14_websocket/) → ... → s17
> *"登录只是第一步。接下来要控制：管理员能删用户，但普通用户只能看。"*
>
> **前提知识**: s12（实现了 JWT 认证，有了 `get_current_user` 依赖）。

---

## 1. 认证 vs 授权

| | 认证 (Authentication) | 授权 (Authorization) |
|---|---|---|
| 问什么 | "你是谁？" | "你能做什么？" |
| 怎么做 | 验证 token/密码 | 检查角色/权限 |
| 失败返回 | 401 Unauthorized | 403 Forbidden |
| s12 做了 | ✅ | ❌ |

---

## 2. RBAC 模型（Role-Based Access Control）

```
User ──> Role ──> Permissions
```

- **User**（用户）：张三
- **Role**（角色）：编辑
- **Permission**（权限）：`users:read`、`posts:write`

一个用户**有一个角色**，一个角色**有多个权限**。

```
角色: admin (管理员)     → 所有权限
角色: editor (编辑)      → 管理文章、查看用户
角色: user (普通用户)    → 查看文章、创建文章
```

---

## 3. 用 Depends 链实现权限检查

这是 s08 学的依赖链的实战应用：

```python
# 第 1 层: 认证（s12）
def get_current_user(token) -> User:
    ...

# 第 2 层: 角色检查
def require_role(*roles: str):
    def checker(user = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(403)
        return user
    return checker  # ← 返回一个依赖函数

# 第 3 层: 权限检查
def require_permission(permission: str):
    def checker(user = Depends(get_current_user)):
        if permission not in get_permissions(user.role):
            raise HTTPException(403)
        return user
    return checker

# 接口里: 声明需要什么权限
@app.delete("/users/{id}")
def delete_user(
    user_id: int,
    admin = Depends(require_role("admin")),  # ← 只有 admin 能访问
):
    ...
```

---

## 4. 权限粒度

```python
# 粗粒度（角色级别）
require_role("admin")        # 管理员能访问

# 细粒度（权限点级别）
require_permission("users:delete")  # 有 users:delete 权限的能访问
```

什么时候用哪个？
- 项目小、角色少 → 角色级别就够了
- 项目大、需要灵活配置 → 权限点级别

---

## 5. 常见错误

### ❌ 在路由函数里手写权限检查

```python
# ❌ 每个接口都重复这段逻辑
@app.get("/admin/users")
def admin_users(user = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(403)
    ...

# ✅ 抽成可复用依赖
@app.get("/admin/users")
def admin_users(admin = Depends(require_role("admin"))):
    ...
```

### ❌ 忘记权限检查

```python
@app.delete("/users/{id}")
def delete_user(id: int, user = Depends(get_current_user)):
    # 忘记检查是不是管理员 → 任何登录用户都能删除！
    ...
```

---

## 6. 自己动手

1. 给 s12 的用户模型加一个 `role` 字段
2. 写一个 `require_role` 依赖函数
3. 写一个管理员专用接口和普通用户接口，测试权限生效
