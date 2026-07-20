# s27-07: 网络排障工具

[← 返回概览](../README.md) | [上一章：WebSocket/SSE](../s06_websocket_sse/) | [下一章：代理/VPN/NAT](../s08_proxy_vpn/)

> *"ping 不通？curl 返回什么？traceroute 走了几跳？网络排障三板斧。"*

---

## 问题 — Agent 调 API 返回 timeout

是网络不通？DNS 解析失败？被防火墙拦了？你需要诊断工具。

---

## 核心工具

### ping — 发个招呼，看对方理不理

```bash
ping api.anthropic.com          # 看通不通，测延迟
ping -c 4 api.anthropic.com     # 发 4 个包
```

ping 发的是 ICMP 包。对方不一定回复（有些服务器关了 ICMP），所以 ping 不通不代表网站挂了。

### nslookup/dig — DNS 查对了没？

```bash
nslookup api.anthropic.com      # DNS 查询
dig api.anthropic.com           # 更详细的 DNS 信息
```

如果 DNS 解析返回了错误的 IP → 可能是 DNS 污染或配置错误。

### curl — HTTP 请求的瑞士军刀

```bash
curl -v https://api.anthropic.com/v1/messages   # -v 看详细过程
curl -I https://api.anthropic.com               # 只看响应头
curl -w "\n%{time_total}\n" url                 # 看总耗时
```

### traceroute — 查数据包走了几站

```bash
traceroute api.anthropic.com  (Linux/macOS)
tracert api.anthropic.com     (Windows)
```

---

## 试一下

```bash
python s27_network/s07_tools/code.py
```

---

## 小结

```
ping     连通性 + 延迟
nslookup DNS 查询
curl     HTTP 测试 (有-v看详细)
traceroute  看路由路径
```
