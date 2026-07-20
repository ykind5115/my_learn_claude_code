#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s28-05: 容器网络

运行: python s28_docker/s05_network/code.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, docker_available, run_docker, print_step,
                   print_note, print_key_point, print_section, print_docker_warning)


def demo_all():
    if not docker_available():
        print_docker_warning()
        print_step(1, "模拟: 容器网络")
        print(f"  $ docker network create mynet")
        print(f"  $ docker run -d --network mynet --name redis redis")
        print(f"  $ docker run --network mynet --name app myapp")
        print(f"  app 内: ping redis -> 通了!")
        print_key_point("自建网络 = 容器间可以用名字通信")
        return

    print_step(1, "端口映射 -p")
    print(f"  docker run -p 8080:80 nginx")
    print(f"  -> 宿主机 8080 端口 -> 容器 80 端口")
    print(f"  -> http://localhost:8080 看到 nginx")
    print_key_point("-p host_port:container_port")

    print_step(2, "Bridge 网络 vs 自建网络")
    print(f"  默认 bridge:")
    print(f"    容器 A (172.17.0.2) -> 只能用 IP 连容器 B (172.17.0.3)")
    print(f"    不能用容器名!")
    print(f"  自建网络:")
    print(f"    docker network create mynet")
    print(f"    容器 A -> ping 容器 B (用名字!) -> DNS 自动解析")

    print_step(3, "网络命令")
    cmds = [
        ("docker network ls", "查看所有网络"),
        ("docker network create name", "创建网络"),
        ("docker network connect net container", "把运行中的容器加入网络"),
        ("docker network inspect net", "查看网络详情"),
    ]
    for cmd, desc in cmds:
        print(f"  {Color.COMMAND}{cmd:40s}{Color.RESET} {desc}")


if __name__ == "__main__":
    print_section("s28-05: 容器网络")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("-p 端口映射, --network 自建网络")
    print_key_point("自建网络 = 容器名自动 DNS 解析")
