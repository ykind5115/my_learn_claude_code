# s28-02: Dockerfile — 写第一个镜像

[← 返回概览](../README.md) | [上一章：Hello Docker](../s01_hello_docker/) | [下一章：层和缓存](../s03_layers_cache/)

> *"怎么把自己的 Python 程序打包成一个 Docker 镜像？3 行就够了。"*

---

## 问题 — 你写了一个 hello.py，怎么给别人跑？

你需要让对方装 Python 3.x、配好环境……或者你给他一个 Docker 镜像，他只需 `docker run`。

---

## 原理：最小 Dockerfile

```dockerfile
FROM python:3.12-slim          # 1. 基础镜像 (Python 3.12 已装好)
COPY hello.py /app/             # 2. 把你的代码放进去
CMD ["python", "/app/hello.py"] # 3. 容器启动时执行这个
```

### 关键指令

| 指令 | 干什么 | 什么时候执行 |
|------|--------|-------------|
| `FROM` | 基于哪个基础镜像 | build 时 |
| `COPY` | 把本地文件复制进镜像 | build 时 |
| `RUN` | 在镜像里执行命令(装依赖等) | build 时 |
| `CMD` | 容器启动时的默认命令 | run 时 |
| `ENTRYPOINT` | 容器入口(不会被覆盖) | run 时 |
| `WORKDIR` | 设置工作目录 | build+run 时 |

---

## 试一下

```bash
python s28_docker/s02_dockerfile/code.py
```

---

## 小结

```dockerfile
FROM python:3.12-slim
COPY hello.py /app/
CMD ["python", "/app/hello.py"]
```
3 行 = 一个可运行的镜像。build -> run -> 搞定。
