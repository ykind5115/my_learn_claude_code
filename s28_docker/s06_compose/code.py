#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s28-06: Docker Compose — 多容器编排

运行: python s28_docker/s06_compose/code.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, docker_available, run_docker, print_step,
                   print_note, print_key_point, print_section, print_docker_warning)


def demo_all():
    if not docker_available():
        print_docker_warning()
        print_step(1, "模拟: docker-compose.yml")
        compose = """version: "3.8"
services:
  app:
    build: .
    ports: ["8000:8000"]
    depends_on: [redis]
  redis:
    image: redis:7-alpine"""
        print(f"  {compose}")
        print_key_point("docker compose up -d -> 一键启动所有服务")
        return

    print_step(1, "docker-compose.yml 结构")
    print(f"  services:       定义容器")
    print(f"    app:          应用容器")
    print(f"      build: .    从当前目录构建")
    print(f"      ports:      端口映射")
    print(f"      depends_on: 依赖 (先启动 redis)")
    print(f"    redis:        Redis 容器")
    print(f"      image:      直接用官方镜像")
    print(f"  volumes:        命名卷 (持久化)")
    print_key_point("一个 yaml = 整个应用栈的定义")

    print_step(2, "Compose 核心命令")
    cmds = [
        ("docker compose up -d", "后台启动所有服务"),
        ("docker compose down", "停止并删除所有容器"),
        ("docker compose logs -f", "实时看所有容器日志"),
        ("docker compose ps", "查看各服务状态"),
        ("docker compose restart app", "重启单个服务"),
    ]
    for cmd, desc in cmds:
        print(f"  {Color.COMMAND}{cmd:35s}{Color.RESET} {desc}")


if __name__ == "__main__":
    print_section("s28-06: Docker Compose")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("docker compose up -d = 一键启动所有服务")
