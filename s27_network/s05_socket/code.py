#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s27-05: Socket 编程 — TCP 客户端/服务端

运行: python s27_network/s05_socket/code.py
"""

import os, sys, socket, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_note, print_section


def demo_1_tcp_echo_server_and_client():
    print_step(1, "TCP Echo: 服务端 + 客户端")

    HOST, PORT = "127.0.0.1", 0  # port=0 → OS 自动分配

    def server():
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        actual_port = server_sock.getsockname()[1]
        print(f"  {Color.INFO}[服务端] 监听 {HOST}:{actual_port}{Color.RESET}")

        # 用 event 通知客户端端口号
        ready.set()
        ready.port = actual_port

        server_sock.settimeout(3)
        try:
            conn, addr = server_sock.accept()
            print(f"  {Color.INFO}[服务端] 客户端连接来自 {addr}{Color.RESET}")
            data = conn.recv(1024)
            print(f"  {Color.INFO}[服务端] 收到: {data.decode()!r}{Color.RESET}")
            conn.sendall(b"ECHO: " + data)
            conn.close()
        except socket.timeout:
            print_note("[服务端] 超时(无客户端连接)")
        server_sock.close()

    ready = threading.Event()
    server_thread = threading.Thread(target=server, daemon=True)
    server_thread.start()
    ready.wait(timeout=2)

    # 客户端
    port = getattr(ready, "port", 9999)
    time.sleep(0.2)
    print(f"  {Color.COMMAND}[客户端] 连接 127.0.0.1:{port}{Color.RESET}")
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_sock.connect(("127.0.0.1", port))
        client_sock.sendall(b"Hello from client!")
        data = client_sock.recv(1024)
        print(f"  {Color.COMMAND}[客户端] 收到: {data.decode()!r}{Color.RESET}")
    except ConnectionRefusedError:
        print_note("[客户端] 连接被拒绝")
    finally:
        client_sock.close()

    server_thread.join(timeout=2)


def demo_2_tcp_boundary():
    print_step(2, "TCP 字节流 — 没有消息边界")
    print(f"  send('hello') 两次")
    print(f"  recv(1024) 可能收到: 'hellohello' (一次)")
    print(f"  也可能收到: 'hel' + 'lohello' (分两次)")
    print(f"  TCP 不保证消息边界!")
    print_note("HTTP 用 Content-Length 头标记边界")
    print_note("WebSocket 用帧(frame)标记边界")


def demo_3_udp_echo():
    print_step(3, "UDP — 不需要连接的通信")
    HOST, PORT = "127.0.0.1", 0
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind((HOST, PORT))
    actual_port = server_sock.getsockname()[1]
    server_sock.settimeout(2)

    # 客户端直接发
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_sock.sendto(b"UDP Hello", ("127.0.0.1", actual_port))
    print(f"  [客户端] UDP 发送 (不需要 connect)")

    try:
        data, addr = server_sock.recvfrom(1024)
        print(f"  [服务端] 收到 UDP: {data.decode()!r} 来自 {addr}")
    except socket.timeout:
        pass
    server_sock.close()
    client_sock.close()
    print_key_point("UDP: 不连接、不确认、不保证送到 → 快但不可靠")


if __name__ == "__main__":
    print_section("s27-05: Socket 编程")
    demo_1_tcp_echo_server_and_client()
    demo_2_tcp_boundary()
    demo_3_udp_echo()
    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("服务端: socket→bind→listen→accept→recv/send")
    print_key_point("客户端: socket→connect→send/recv")
    print_key_point("TCP=字节流无边界 UDP=发出去不管")
