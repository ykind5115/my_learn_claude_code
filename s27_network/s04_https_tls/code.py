#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s27-04: HTTPS/TLS — 加密通道

运行: python s27_network/s04_https_tls/code.py
"""

import os, sys, ssl, socket
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_note, print_section


def demo_1_why_https():
    print_step(1, "为什么需要 HTTPS？")
    print(f"  HTTP (明文):")
    print(f"    你 ──POST /v1/messages──→ api.anthropic.com")
    print(f"           ↑                                    ")
    print(f"        中间路由器能看到: API Key + 你的消息!       ")
    print(f"  {Color.SUCCESS}HTTPS (加密):{Color.RESET}")
    print(f"    你 ══加密通道══ api.anthropic.com")
    print(f"         ↑                                    ")
    print(f"      中间路由器只能看到: 你在和 anthropic 通信")


def demo_2_certificate_check():
    print_step(2, "Python 检查服务器证书")
    host = "api.anthropic.com"
    port = 443
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                print(f"  服务器: {Color.BOLD}{host}:{port}{Color.RESET}")
                print(f"  TLS 版本: {ssock.version()}")
                print(f"  证书主体: {cert.get('subject', 'N/A')}")
                print(f"  证书颁发者: {cert.get('issuer', 'N/A')}")
                print(f"  有效期: {cert.get('notBefore', '?')} ~ {cert.get('notAfter', '?')}")
                print_key_point("Python 自动验证了证书链 — 不需要你做任何事")
    except Exception as e:
        print_note(f"连接失败: {e}")
        print_note("(可能无网络，但概念不变)")


def demo_3_tls_handshake():
    print_step(3, "TLS 握手过程 (简化)")
    steps = [
        "ClientHello: 客户端说 '我支持 TLS 1.3, AES, RSA...'",
        "ServerHello: 服务器回应 '我用 TLS 1.3, 这是我的证书'",
        "验证证书: 检查 CA 签名、域名匹配、是否过期",
        "密钥交换: 用服务器公钥加密'会话密钥'发过去",
        "加密通道: 之后所有数据用对称加密传输",
    ]
    for i, s in enumerate(steps, 1):
        print(f"  {i}. {s}")


def demo_4_encryption_types():
    print_step(4, "非对称 vs 对称加密")
    print(f"  非对称加密 (RSA/ECDSA):")
    print(f"    公钥加密 → 私钥解密 (一把锁两把钥匙)")
    print(f"    慢但安全 → 用于 TLS 握手")
    print(f"  对称加密 (AES):")
    print(f"    同一把钥匙加密和解密")
    print(f"    快 → 用于传输数据")
    print_key_point("TLS = 非对称认证 + 对称传输")


if __name__ == "__main__":
    print_section("s27-04: HTTPS/TLS — 加密通道")
    demo_1_why_https()
    demo_2_certificate_check()
    demo_3_tls_handshake()
    demo_4_encryption_types()
    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("HTTPS = HTTP + TLS 加密")
    print_key_point("TLS握手: 验证证书 → 交换密钥 → 加密通道")
    print_key_point("Agent 的 API Key 靠 TLS 保护不被窃取")
