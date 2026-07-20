#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s28-03: 层和缓存

运行: python s28_docker/s03_layers_cache/code.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, docker_available, run_docker, print_step,
                   print_note, print_key_point, print_section, print_docker_warning)


def demo_all():
    if not docker_available():
        print_docker_warning()
        print_step(1, "模拟: 层缓存机制")
        print(f"  Layer 1: FROM python:3.12-slim  (缓存)")
        print(f"  Layer 2: RUN pip install numpy   (缓存)")
        print(f"  Layer 3: COPY requirements.txt   (缓存)")
        print(f"  Layer 4: RUN pip install -r reqs (缓存)")
        print(f"  Layer 5: COPY . /app/            <- 代码变了，重建!")
        print(f"  Layer 6: CMD [python, app.py]    <- 也重建!")
        print_key_point("不变的放前面(依赖) -> 常变的放后面(代码)")
        return

    print_step(1, "层 = 每条指令一个 Layer")
    print(f"  FROM    -> Layer 1")
    print(f"  RUN     -> Layer 2")
    print(f"  COPY    -> Layer 3")
    print(f"  CMD     -> Layer 4 (最后一层)")
    print_key_point("改一层 -> 它和之后的所有层都重建")

    print_step(2, "缓存规则")
    print(f"  坏顺序 (每次都重建依赖):")
    print(f"    COPY . /app/           <- 代码变了")
    print(f"    RUN pip install -r ...  <- 必须重装!")
    print(f"  好顺序 (依赖不变就用缓存):")
    print(f"    COPY requirements.txt . <- 很少变")
    print(f"    RUN pip install -r ...  <- 用缓存!")
    print(f"    COPY . /app/           <- 只重建这一层")

    print_step(3, ".dockerignore")
    print(f"  排除不需要的文件, 加速 COPY:")
    print(f"    __pycache__/")
    print(f"    venv/")
    print(f"    .git/")
    print(f"    *.pyc")


if __name__ == "__main__":
    print_section("s28-03: 层和缓存")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("Layer = 每条指令, 有缓存")
    print_key_point("不变的放前面, 常变的放后面")
