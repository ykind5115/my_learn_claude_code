# s17: 部署 — 从本地到服务器，一步到位

s01 → ... → s16 → `s17`
> *"写完代码只完成了 50% — 部署上线让别人也能用，才算真正完成。"*
>
> **前提知识**: s01-s16（有完整的 API 应用可以部署）。

---

## 1. 生产部署检查清单

| 检查项 | 为什么重要 |
|--------|-----------|
| ✅ 关闭 DEBUG 模式 | 生产环境不能暴露调试信息 |
| ✅ 用 Gunicorn 管理多个 worker | 一个进程挂了其他的继续服务 |
| ✅ 环境变量管理配置 | 密码和密钥不能硬编码 |
| ✅ 健康检查端点 | 负载均衡器需要知道实例是否活着 |
| ✅ Docker 容器化 | 环境一致性，任何机器都能跑 |
| ✅ 隐藏 `/docs` | 生产环境不应该暴露 API 文档 |

---

## 2. 推荐架构

```
Internet → Nginx (443) → Gunicorn → Uvicorn workers × 4
              ↑ 反向代理    ↑ 进程管理    ↑ 实际处理请求
```

- **Nginx**：处理 SSL、静态文件、限流、负载均衡
- **Gunicorn**：管理多个 Uvicorn worker 进程
- **Uvicorn workers**：实际处理 HTTP → FastAPI

---

## 3. Docker 部署

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t my-api .
docker run -p 8000:8000 my-api
```

---

## 4. 关键：健康检查

```python
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    # 检查数据库连接
    db_ok = check_database()
    if db_ok:
        return {"status": "ready"}
    else:
        return JSONResponse(status_code=503, content={"status": "not ready"})
```

- `/health`：服务是否还活着（Kubernetes liveness probe）
- `/ready`：是否准备好接受流量（Kubernetes readiness probe）

---

## 5. 环境变量

```python
# ❌ 生产环境绝对不能这样
SECRET_KEY = "my-secret-key"

# ✅ 从环境变量读取
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY 环境变量未设置")
```

---

## 6. 自己动手

1. 给 s12 的 JWT code.py 写一个 Dockerfile
2. 用 `docker build` + `docker run` 在容器里启动 API
3. 添加 `/health` 健康检查端点
4. 把 `SECRET_KEY` 改成从环境变量读取
