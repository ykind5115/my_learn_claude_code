# s28: Docker 基础 — 把软件装进集装箱

[中文](README.md)

> *"Docker 不是虚拟机。Docker 是软件集装箱——把代码、依赖、配置打包成一个标准单元，在任何地方都能原样运行。"*

本课程面向 **Docker 零基础**的学习者。不假设你用过容器。
每一章只用 Dockerfile 的一小部分，每一步都用「集装箱」模型解释「为什么」。
最终目标：能把自己的 **Agent 应用打包成 Docker 镜像**，在任何机器上跑起来。

---

## 为什么大多数 Docker 教程让人学不会？

一上来就甩一堆概念：Image、Container、Dockerfile、Layer、Volume、Network、Compose、Registry……全是名词。然后让你抄一个 50 行的 Dockerfile。

你抄完了，跑了，但不知道为什么这 50 行每个词在做什么。

**本课程反其道而行之**：先用 s00 建立「软件集装箱」的心智模型。然后 s01 只跑一行 `docker run hello-world`。s02 只写 3 行 Dockerfile。每章只加一个新概念。

---

## 开始之前：你需要什么基础？

- Python 基础
- 安装了 Docker Desktop（Windows/Mac）或 Docker Engine（Linux）
- `docker` 命令在 PATH 中可用

> 从 [s00](s00_mental_model/) 开始 — 纯概念。

---

## 学习路线图

```
s00  心智模型：软件集装箱         <- 纯概念
s01  Hello Docker                <- docker run hello-world
s02  Dockerfile                  <- 3 行 Dockerfile
s03  层和缓存                     <- 为什么第二次 build 快
s04  数据持久化                   <- Volume: 容器删了数据在
s05  容器网络                     <- 两个容器怎么通信
s06  Docker Compose              <- 多容器一键启动
s07  多阶段构建                   <- 1GB -> 100MB
s08  Agent 容器化                 <- 完整实战
```

---

## 模块总览

### 第 0 章：心智模型

| # | 模块 | 要解决的问题 | 不写代码 |
|---|------|-------------|---------|
| s00 | [软件集装箱](s00_mental_model/) | "Docker 到底是什么？" | YES |

### 第 1 章：镜像与容器

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s01 | [Hello Docker](s01_hello_docker/) | "怎么跑第一个容器？" | run, ps, exec, stop |
| s02 | [Dockerfile](s02_dockerfile/) | "怎么打包自己的程序？" | FROM, COPY, CMD |
| s03 | [层和缓存](s03_layers_cache/) | "为什么第二次 build 快？" | layer, cache, .dockerignore |

### 第 2 章：数据与网络

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s04 | [数据持久化](s04_volumes/) | "容器删了数据在吗？" | volume, bind mount |
| s05 | [容器网络](s05_network/) | "两个容器怎么通信？" | bridge, port mapping |

### 第 3 章：生产级实战

| # | 模块 | 要解决的问题 | 核心概念 |
|---|------|-------------|----------|
| s06 | [Docker Compose](s06_compose/) | "怎么编排多容器？" | compose.yml, services |
| s07 | [多阶段构建](s07_multistage/) | "镜像怎么瘦身？" | multi-stage, distroless |
| s08 | [Agent 容器化](s08_agent_docker/) | "Agent 怎么打包？" | 完整 Dockerfile + compose |

---

## 快速开始

```bash
# 1. 先确认 Docker 可用
docker --version

# 2. 从 s00 概念章开始
# 打开 s28_docker/s00_mental_model/README.md

# 3. 运行第一个演示
python s28_docker/s01_hello_docker/code.py
```

---

## 跟 Agent 的关系

| Docker 概念 | Agent 场景 |
|------------|-----------|
| Dockerfile | 把 Agent 应用打包成可复现的镜像 |
| Volume | Agent 的 memory/日志持久化 |
| Network | Agent 团队容器间通信 |
| Compose | Agent + Redis + DB 一键启动 |
| 多阶段构建 | 生产级 Agent 镜像瘦身 |
