# s28-05: 容器网络

[← 返回概览](../README.md) | [上一章：数据持久化](../s04_volumes/) | [下一章：Docker Compose](../s06_compose/)

> *"两个容器怎么互相通信？容器怎么让外面访问到？"*

---

## 问题 — 你的 App 容器需要连 Redis 容器

Redis 跑在一个容器里，App 跑在另一个容器里。它们怎么找到对方？

---

## 原理：Docker 网络模型

### 默认 Bridge 网络

```
Host (你的电脑)
  ├── 容器 A (app, 172.17.0.2)
  │     └ 想连 Redis? -> redis:6379
  │         需要 DNS 解析!
  └── 容器 B (redis, 172.17.0.3)
```

在默认 bridge 网络上，容器之间**不能用名字**互相访问（只有 IP）。需要自建网络。

### 自建网络

```bash
docker network create mynet
docker run --network mynet --name redis redis
docker run --network mynet --name app myapp
# app 里直接 ping redis -> 通了! (DNS 自动解析容器名)
```

### 端口映射

```bash
docker run -p 8080:80 nginx
# 宿主机 8080 -> 容器 80
# 浏览器 http://localhost:8080 -> nginx
```

---

## 试一下

```bash
python s28_docker/s05_network/code.py
```

---

## 小结

```
-p 8080:80      端口映射 (外面->容器)
--network mynet  自建网络 (容器间用名字通信)
bridge           默认网络 (只有 IP，不能用名字)
```
