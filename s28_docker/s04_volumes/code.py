#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s28-04: 数据持久化 — Volume

运行: python s28_docker/s04_volumes/code.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, docker_available, run_docker, print_step,
                   print_note, print_key_point, print_section, print_docker_warning)


def demo_all():
    if not docker_available():
        print_docker_warning()
        print_step(1, "模拟: Volume 演示")
        print(f"  $ docker volume create mydata")
        print(f"  $ docker run -v mydata:/data alpine sh")
        print(f"  # echo 'important' > /data/note.txt")
        print(f"  $ docker rm container  (删除容器)")
        print(f"  $ docker run -v mydata:/data alpine cat /data/note.txt")
        print(f"  -> 'important' (数据还在!)")
        print_key_point("Volume = 集装箱外挂仓库")
        return

    print_step(1, "三种挂载方式")
    print(f"  Volume:    docker run -v myvol:/data ...")
    print(f"             Docker 管理, /var/lib/docker/volumes/")
    print(f"  Bind Mount: docker run -v /host/path:/container/path ...")
    print(f"             直接映射宿主机目录")
    print(f"  tmpfs:     docker run --tmpfs /tmp ...")
    print(f"             内存临时存储, 关容器就没了")

    print_step(2, "Volume 演示")
    # 创建 volume
    ret, out, _ = run_docker(["volume", "create", "s28-demo-vol"])
    print(f"  $ docker volume create s28-demo-vol -> {'OK' if ret == 0 else 'exists'}")

    # 写数据
    ret, out, _ = run_docker(
        ["run", "--rm", "-v", "s28-demo-vol:/data", "alpine",
         "sh", "-c", "echo persisted > /data/demo.txt && cat /data/demo.txt"]
    )
    if ret == 0:
        print(f"  $ 写入并验证: {out.strip()!r}")

    # 删除容器后读数据
    ret, out, _ = run_docker(
        ["run", "--rm", "-v", "s28-demo-vol:/data", "alpine",
         "cat", "/data/demo.txt"]
    )
    if ret == 0:
        print(f"  $ 新容器读数据: {out.strip()!r}")
        print_key_point("容器删了, Volume 里的数据还在!")

    # 清理
    run_docker(["volume", "rm", "s28-demo-vol"])


if __name__ == "__main__":
    print_section("s28-04: 数据持久化 — Volume")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("Volume: 容器删了数据在 (推荐)")
    print_key_point("Bind Mount: 开发时映射代码目录")
