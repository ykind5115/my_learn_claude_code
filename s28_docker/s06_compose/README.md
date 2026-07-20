# s28-06: Docker Compose — 多容器编排

[← 返回概览](../README.md) | [上一章：容器网络](../s05_network/) | [下一章：多阶段构建](../s07_multistage/)

> *"一个 App + Redis + PostgreSQL，每次手动启动三个容器太烦了。一个 yaml 文件，一条命令全部搞定。"*

---

## 问题 — 你的应用依赖 Redis 和 PostgreSQL

每次都要记着先启动 Redis，再启动 PostgreSQL，再启动 App，还得保证它们在同一网络。人脑不适合做这个——让 Compose 来。

---

## 原理：一个 yaml 描述整个应用栈

```yaml
# docker-compose.yml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - db
  redis:
    image: redis:7-alpine
  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: secret

volumes:
  pgdata:
```

一条命令：`docker compose up -d` → 网络自动创建、容器按依赖顺序启动、Volume 自动管理。

---

## 试一下

```bash
python s28_docker/s06_compose/code.py
```

---

## 小结

```bash
docker compose up -d     后台启动所有服务
docker compose down      停止并删除所有容器
docker compose logs -f   看日志
docker compose ps        查看状态
```
