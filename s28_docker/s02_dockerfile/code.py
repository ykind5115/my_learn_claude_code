#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s28-02: Dockerfile — 写第一个镜像

运行: python s28_docker/s02_dockerfile/code.py
"""

import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, docker_available, run_docker, print_step,
                   print_output, print_note, print_key_point, print_section,
                   print_docker_warning)


def demo_all():
    if not docker_available():
        print_docker_warning()
        print_step(1, "模拟: 3 行 Dockerfile")
        print(f"  Dockerfile:")
        print(f"    FROM python:3.12-slim")
        print(f"    COPY hello.py /app/")
        print(f'    CMD ["python", "/app/hello.py"]')
        print_key_point("3 行 = 一个可运行的 Python 镜像")
        return

    # 创建临时工作区
    workdir = Path(tempfile.mkdtemp(prefix="s28_demo_"))

    # 写 hello.py
    hello_py = workdir / "hello.py"
    hello_py.write_text("print('Hello from Docker!')\n")
    print(f"  hello.py: {hello_py.read_text().strip()}")

    # 写 Dockerfile
    dockerfile = workdir / "Dockerfile"
    dockerfile.write_text("""FROM python:3.12-slim
COPY hello.py /app/
WORKDIR /app
CMD ["python", "hello.py"]
""")
    print_step(1, f"Dockerfile ({dockerfile})")
    for line in dockerfile.read_text().strip().split("\n"):
        print(f"  {Color.COMMAND}{line}{Color.RESET}")

    # Build
    print_step(2, "docker build")
    tag = "s28-demo-hello:latest"
    ret, out, err = run_docker(["build", "-t", tag, "-f", str(dockerfile), str(workdir)], timeout=120)
    if ret == 0:
        print_output(out)
        print_key_point("Build 成功!")
    else:
        print_note(f"Build 失败: {err[:300]}")
        import shutil; shutil.rmtree(workdir, ignore_errors=True)
        return

    # Run
    print_step(3, "docker run")
    ret, out, err = run_docker(["run", "--rm", tag])
    if ret == 0:
        print(f"  {Color.SUCCESS}容器输出: {out.strip()}{Color.RESET}")
    else:
        print_note(f"Run 失败: {err[:200]}")

    # 清理
    run_docker(["rmi", "-f", tag])
    import shutil; shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    print_section("s28-02: Dockerfile")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("FROM -> COPY -> CMD = 3 行 Dockerfile")
    print_key_point("docker build -t name . -> docker run name")
