# s28-00: 心智模型 — 软件集装箱

[← 返回概览](../README.md) | [下一章：Hello Docker](../s01_hello_docker/)

> *Docker = 标准化集装箱。把你的软件和它需要的所有东西打包成一个箱子，到任何港口都能原样卸货运行。*

---

## 问题 — "在我机器上能跑啊！"

你写了一个 Python 应用，依赖 Python 3.12 + Redis + 一堆系统库。交给同事——他 Python 3.10，Redis 版本不一样，跑不起来。

Docker 解决的就是这个问题：**"把你的机器也打包进去"**。

---

## 核心模型：集装箱 vs 虚拟机

```
虚拟机:                          Docker:
┌─────────────────────┐         ┌─────────────────────┐
│ App A  │ App B      │         │ App A  │ App B      │
├────────┴────────────┤         ├────────┴────────────┤
│ Guest OS (完整 OS)   │         │ Docker Engine        │
├─────────────────────┤         ├──────────────────────┤
│ Hypervisor           │         │ Host OS (共享内核)    │
├─────────────────────┤         ├──────────────────────┤
│ Host OS              │         │ Hardware              │
├─────────────────────┤         └──────────────────────┘
│ Hardware              │
└─────────────────────┘
每个 VM 自带完整 OS (~GB)        每个容器只打包应用+依赖 (~MB)
```

---

## 核心角色

| 概念 | 集装箱比喻 | 一句话 |
|------|-----------|--------|
| **镜像 (Image)** | 集装箱设计图纸 | 只读模板，定义了箱子里有什么 |
| **容器 (Container)** | 正在用的集装箱 | 镜像的运行实例 |
| **Dockerfile** | 制造说明书 | FROM 基础材料、RUN 加工、COPY 装货 |
| **层 (Layer)** | 制造步骤 | 每条指令生成一层，层有缓存 |
| **Volume** | 外挂仓库 | 容器删了，仓库里的数据还在 |
| **Network** | 集装箱间管道 | 容器之间怎么通信 |
| **Registry** | 集装箱码头 | Docker Hub = 全球集装箱调度中心 |

---

## 一张图记住

```
Dockerfile (说明书)
    │
    ▼ docker build
Image (图纸)
    │
    ▼ docker run
Container (运行的箱子)
    │  docker exec (进箱子)
    │  docker stop (关箱子)
    │  docker rm   (丢箱子, 但 Volume 里的数据还在)
```

---

## 准备好了吗？

打开 [s01: Hello Docker](../s01_hello_docker/)，跑你的第一个集装箱。

> *"It works on my machine" → "Then we'll ship your machine"*
