# s28-08: Agent 容器化实战

[← 返回概览](../README.md) | [上一章：多阶段构建](../s07_multistage/)

> *"把前面学的全串起来：写一个 Agent 应用，打包成镜像，用 Compose 编排依赖，跑起来。"*

---

## 问题 — 把 Agent 应用部署到任何地方

你的 Agent 应用需要 Python 3.12 + anthropic SDK + Redis(会话缓存) + 一些系统工具。怎么让它在任何机器上都能跑？

---

## 实战方案

```
agent-app/
├── Dockerfile           # Agent 镜像
├── docker-compose.yml   # app + redis
├── requirements.txt     # anthropic, redis, ...
├── .dockerignore
└── agent.py             # Agent 主程序
```

### Dockerfile (多阶段)

```dockerfile
FROM python:3.12-slim AS builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.12-slim
COPY --from=builder /root/.local /root/.local
COPY agent.py /app/
WORKDIR /app
ENV ANTHROPIC_API_KEY=""
CMD ["python", "agent.py"]
```

### docker-compose.yml

```yaml
services:
  agent:
    build: .
    env_file: .env
    depends_on: [redis]
  redis:
    image: redis:7-alpine
    volumes: [redis_data:/data]
volumes:
  redis_data:
```

---

## 试一下

```bash
python s28_docker/s08_agent_docker/code.py
```

---

## 小结

```
Agent 容器化 = Dockerfile + Compose + .env
多阶段构建瘦身
Compose 编排依赖 (Redis/DB)
.env 注入 API Key (不进镜像!)
```
