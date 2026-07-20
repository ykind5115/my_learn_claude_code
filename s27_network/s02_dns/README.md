# s27-02: DNS — 互联网的电话簿

[← 返回概览](../README.md) | [上一章：TCP/IP 模型](../s01_tcp_ip_model/) | [下一章：HTTP 深入](../s03_http_deep/)

> *"怎么把 `api.anthropic.com` 变成 IP 地址？"*

---

## 问题 — 你记住了 `api.anthropic.com`，但网络只认 IP 地址

计算机之间通信用的是 IP 地址（`1.2.3.4`），不是域名。所以在你发 HTTP 请求之前，先得查 DNS——把域名翻译成 IP。

---

## 原理：邮局查询台

```
你: "api.anthropic.com 在哪？"
     │
     ▼
DNS 递归解析器 (本地/ISP)
     │ 不知道 → 问根服务器
     ▼
根 DNS: "我不知道，但 .com 的服务器知道"
     │
     ▼
.com DNS: "不知道具体地址，但 anthropic 的 DNS 知道"
     │
     ▼
anthropic DNS: "api.anthropic.com → 1.2.3.4"
     │
     ▼
解析器记住了 (缓存)，下次直接返回
```

### DNS 记录类型

| 类型 | 查什么 | 示例 |
|------|--------|------|
| A | 域名→IPv4 | `api.example.com → 1.2.3.4` |
| AAAA | 域名→IPv6 | `→ 2600:1f18:...` |
| CNAME | 别名→真名 | `www.example.com → example.com` |
| MX | 邮件服务器 | `→ mail.example.com` |

---

## 试一下

```bash
python s27_network/s02_dns/code.py
```

---

## 小结

```
DNS = 互联网电话簿
域名 → DNS 查询 → IP 地址
A 记录: IPv4, AAAA 记录: IPv6
getaddrinfo() = Python 的 DNS 查询
```
