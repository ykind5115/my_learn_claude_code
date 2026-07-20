#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s28-01: Hello Docker — 第一个容器

运行: python s28_docker/s01_hello_docker/code.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, docker_available, run_docker, print_step,
                   print_output, print_note, print_key_point, print_section,
                   print_docker_warning)


def demo_all():
    if not docker_available():
        print_docker_warning()
        print_step(1, "模拟: docker run hello-world")
        print(f"  $ docker run hello-world")
        print(f"  Hello from Docker!")
        print(f"  This message shows that your installation appears to be working correctly.")
        print_step(2, "模拟: docker ps")
        print(f"  CONTAINER ID   IMAGE         STATUS")
        print(f"  (空 — 容器跑完就退出了)")
        print_key_point("hello-world 容器输出消息后自动退出")
        return

    print_step(1, "docker run hello-world")
    ret, out, err = run_docker(["run", "--rm", "hello-world"])
    print_output(out, max_lines=15)
    if ret != 0:
        print_note(f"可能需要先 pull: docker pull hello-world")
        ret2, out2, _ = run_docker(["pull", "hello-world"], timeout=60)
        if ret2 == 0:
            ret, out, _ = run_docker(["run", "--rm", "hello-world"])
            print_output(out, max_lines=15)

    print_step(2, "docker ps — 查看运行中的容器")
    ret, out, _ = run_docker(["ps"])
    print_output(out)
    print_note("hello-world 跑完就退出了，所以 ps 看不到它。加 -a 看全部:")

    ret, out, _ = run_docker(["ps", "-a", "--format", "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"])
    lines = [l for l in out.strip().split("\n") if "hello-world" in l.lower()]
    if lines:
        for l in lines:
            print(f"  {Color.DIM}{l}{Color.RESET}")

    print_step(3, "docker images — 本地镜像列表")
    ret, out, _ = run_docker(["images", "--format", "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"])
    lines = [l for l in out.strip().split("\n") if "hello-world" in l.lower()][:3]
    for l in lines:
        print(f"  {Color.DIM}{l}{Color.RESET}")


if __name__ == "__main__":
    print_section("s28-01: Hello Docker")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("docker run = 创建并启动容器")
    print_key_point("docker ps = 查看运行中的容器")
    print_key_point("hello-world 跑完自动退出")
