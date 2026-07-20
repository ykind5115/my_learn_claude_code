# s28-03: 层和缓存

[← 返回概览](../README.md) | [上一章：Dockerfile](../s02_dockerfile/) | [下一章：数据持久化](../s04_volumes/)

> *"为什么第二次 docker build 只要 0.5 秒？因为 Docker 把每一步的结果缓存了。"*

---

## 问题 — 改了代码，重新 build，又要 5 分钟？

不改的部分为什么还要重新构建？Docker 的**层缓存**机制解决了这个问题。

---

## 原理：每条指令是一层

```dockerfile
FROM python:3.12-slim          # Layer 1: 基础层 (来自 registry)
RUN pip install numpy           # Layer 2: 装依赖 (很少变)
RUN pip install pandas           # Layer 3: 装依赖
COPY requirements.txt /app/     # Layer 4: 只复制依赖文件
RUN pip install -r /app/requirements.txt  # Layer 5: 装所有依赖
COPY . /app/                    # Layer 6: 复制代码 (经常变!)
CMD ["python", "app.py"]
```

**缓存规则**：如果某一层变了，它和它之后的所有层都重新构建。所以要把**不变的放前面，常变的放后面**。

上面的顺序是错的！应该是：

```dockerfile
COPY requirements.txt /app/     # <- 先复制依赖文件(很少变)
RUN pip install -r /app/requirements.txt  # <- 依赖不变，这层就用缓存
COPY . /app/                    # <- 代码最后复制(经常变)
```

---

## 试一下

```bash
python s28_docker/s03_layers_cache/code.py
```

---

## 小结

```
每条指令 = 一层 Layer
层有缓存: 没变就用缓存，变了就重建
优化: 不变的(依赖)放前面，常变的(代码)放最后
.dockerignore: 排除不需要的文件(venv, .git, __pycache__)
```
