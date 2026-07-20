# s28-04: 数据持久化 — Volume

[← 返回概览](../README.md) | [上一章：层和缓存](../s03_layers_cache/) | [下一章：容器网络](../s05_network/)

> *"容器删了，里面的数据还在吗？不在。除非你用了 Volume。"*

---

## 问题 — 数据库跑在容器里，容器删了数据全丢？

容器是无状态的——删了就没了。Volume 让你把数据存在**容器外面**。

---

## 原理：三种挂载方式

```
Bind Mount:                       Volume:
/data/on/host ←→ /data/in/container    named_volume ←→ /data/in/container
(宿主机路径)                          (Docker 管理的)

tmpfs:
内存临时文件系统 ←→ /tmp/in/container
(关容器就没, 但超快)
```

### 什么时候用什么

| 方式 | 持久化 | 用途 |
|------|--------|------|
| Volume | YES | 数据库数据、日志 (推荐) |
| Bind Mount | YES | 开发时实时同步代码 |
| tmpfs | NO | 临时缓存 (不需要持久) |

---

## 试一下

```bash
python s28_docker/s04_volumes/code.py
```

---

## 小结

```
容器删了数据没了? -> 用 Volume
Volume: Docker 管理, 独立于容器
Bind Mount: 直接映射宿主机路径
tmpfs: 内存临时存储
```
