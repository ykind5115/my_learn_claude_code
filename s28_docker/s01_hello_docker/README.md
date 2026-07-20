# s28-01: Hello Docker

[← 返回概览](../README.md) | [下一章：Dockerfile](../s02_dockerfile/)

> *"docker run hello-world — 一行命令，跑起人生第一个容器。"*

---

## 问题 — Docker 装好了，然后呢？

验证 Docker 能用，理解 `run`、`ps`、`exec`、`stop` 四个最基本的命令。

---

## 核心命令

| 命令 | 干什么 | 集装箱比喻 |
|------|--------|-----------|
| `docker run image` | 根据图纸造箱子并启动 | 下单造箱+装货 |
| `docker ps` | 查看正在运行的箱子 | 码头清点 |
| `docker ps -a` | 查看所有箱子(含已停) | 查历史记录 |
| `docker exec -it` | 进入正在运行的箱子 | 钻进箱子内部 |
| `docker stop` | 停止箱子 | 关箱 |
| `docker rm` | 删除已停的箱子 | 丢箱 |
| `docker images` | 查看本地图纸 | 图纸清单 |

---

## 试一下

```bash
python s28_docker/s01_hello_docker/code.py
```

---

## 小结

```
docker run hello-world   跑第一个容器
docker ps                看看谁在跑
docker exec -it xxx sh   钻进容器
docker stop xxx          关了
docker rm xxx            扔了
```
