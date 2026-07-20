#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s28-07: 多阶段构建 — 镜像瘦身

运行: python s28_docker/s07_multistage/code.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, docker_available, run_docker, print_step,
                   print_note, print_key_point, print_section, print_docker_warning)


def demo_all():
    if not docker_available():
        print_docker_warning()
        print_step(1, "模拟: 多阶段 Dockerfile")
        multi = """# Stage 1: 构建 (大)
FROM python:3.12 AS builder
RUN pip install --user numpy pandas

# Stage 2: 运行 (小)
FROM python:3.12-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
CMD ["python", "/app/main.py"]"""
        print(f"  {multi}")
        print_key_point("最终镜像 = Stage 2 的大小, Stage 1 被丢弃")
        return

    print_step(1, "单阶段 vs 多阶段")
    print(f"  单阶段:")
    print(f"    FROM python:3.12  (800MB, 含编译器/git/curl)")
    print(f"    RUN apt install gcc make ...  (+200MB)")
    print(f"    RUN pip install ...           (+100MB)")
    print(f"    最终: ~1.2GB")
    print(f"  多阶段:")
    print(f"    Stage 1: FROM python:3.12 AS builder")
    print(f"             编译、安装... (1.2GB, 但会被丢弃)")
    print(f"    Stage 2: FROM python:3.12-slim (150MB)")
    print(f"             COPY --from=builder (只复制产物)")
    print(f"             最终: ~200MB")

    print_step(2, "常用瘦身技巧")
    tips = [
        "python:3.12-slim (150MB) 代替 python:3.12 (800MB)",
        "python:3.12-alpine (50MB) 更小但可能缺库",
        "多阶段: build 阶段用大镜像, run 阶段用小镜像",
        ".dockerignore: 排除 venv/ .git/ __pycache__/",
        "RUN apt clean && rm -rf /var/lib/apt/lists/*",
    ]
    for t in tips:
        print(f"  {Color.DIM}- {t}{Color.RESET}")


if __name__ == "__main__":
    print_section("s28-07: 多阶段构建")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("多阶段 = 构建用大的, 运行用小的")
    print_key_point("slim > alpine (兼容性好)")
