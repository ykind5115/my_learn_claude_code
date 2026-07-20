# s28-07: 多阶段构建 — 镜像瘦身

[← 返回概览](../README.md) | [上一章：Docker Compose](../s06_compose/) | [下一章：Agent 容器化](../s08_agent_docker/)

> *"编译需要 1GB 的工具链，但运行只需要 50MB 的二进制。多阶段构建让你只把运行需要的打包进去。"*

---

## 问题 — 你的 Python 镜像有 1.2GB

为什么这么大？因为基础镜像带了编译器、git、curl……而你的应用其实只需要 Python 运行时 + 依赖 + 代码。

---

## 原理：两个 FROM

```dockerfile
# Stage 1: 构建阶段 (大镜像，有编译器)
FROM python:3.12 AS builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: 运行阶段 (小镜像，只复制构建产物)
FROM python:3.12-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
CMD ["python", "/app/main.py"]
```

- Stage 1 用完整镜像编译/安装
- Stage 2 只复制**运行需要的东西**
- 最终镜像 = Stage 2 的大小（Stage 1 被丢弃）

---

## 试一下

```bash
python s28_docker/s07_multistage/code.py
```

---

## 小结

```
多阶段构建: 多个 FROM
Stage 1: 编译/安装 (大)
Stage 2: 只复制产物 (小)
COPY --from=builder 跨阶段复制
最终镜像 = 最后一个 FROM 的大小
```
