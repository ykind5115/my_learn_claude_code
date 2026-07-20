#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s28-08: Agent 容器化实战

运行: python s28_docker/s08_agent_docker/code.py
"""

import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, docker_available, run_docker, print_step,
                   print_note, print_key_point, print_section, print_docker_warning)


def demo_all():
    if not docker_available():
        print_docker_warning()
        print_step(1, "模拟: Agent Dockerfile")
        print(f"  FROM python:3.12-slim")
        print(f"  COPY requirements.txt .")
        print(f"  RUN pip install anthropic redis")
        print(f"  COPY agent.py /app/")
        print(f'  CMD ["python", "/app/agent.py"]')
        print_key_point("Agent 镜像 = Python + SDK + 你的代码")
        return

    # 创建演示工作区
    workdir = Path(tempfile.mkdtemp(prefix="s28_agent_"))

    # requirements.txt
    (workdir / "requirements.txt").write_text("anthropic>=0.39.0\nredis>=5.0.0\n")

    # agent.py (简化)
    (workdir / "agent.py").write_text("""#!/usr/bin/env python3
\"\"\"Minimal Agent demo\"\"\"
import os
print(f"Agent starting...")
print(f"API Key configured: {'Yes' if os.environ.get('ANTHROPIC_API_KEY') else 'No'}")
print(f"Redis host: {os.environ.get('REDIS_HOST', 'redis')}")
print("Agent ready.")
""")

    # Dockerfile
    dockerfile = workdir / "Dockerfile"
    dockerfile.write_text("""FROM python:3.12-slim AS builder
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
COPY --from=builder /root/.local /root/.local
COPY agent.py /app/
WORKDIR /app
ENV ANTHROPIC_API_KEY=""
ENV REDIS_HOST=redis
CMD ["python", "agent.py"]
""")

    print_step(1, f"项目结构 ({workdir})")
    for f in sorted(workdir.iterdir()):
        if f.name != "__pycache__":
            print(f"  {f.name}")

    print_step(2, "Dockerfile")
    for line in dockerfile.read_text().strip().split("\n"):
        print(f"  {Color.COMMAND}{line}{Color.RESET}")

    # Build
    print_step(3, "docker build")
    tag = "s28-agent-demo:latest"
    ret, out, err = run_docker(["build", "-t", tag, "-f", str(dockerfile), str(workdir)], timeout=180)
    if ret == 0:
        # 只显示最后的行
        lines = out.strip().split("\n")
        for l in lines[-5:]:
            print(f"  {Color.DIM}{l}{Color.RESET}")
        print_key_point("Build 成功!")
    else:
        print_note(f"Build 失败 (可能网络问题下载不了): {err[:200]}")
        import shutil; shutil.rmtree(workdir, ignore_errors=True)
        return

    # Run
    print_step(4, "docker run")
    ret, out, err = run_docker(["run", "--rm", "-e", "ANTHROPIC_API_KEY=demo-key", tag])
    if ret == 0:
        for line in out.strip().split("\n"):
            print(f"  {Color.SUCCESS}{line}{Color.RESET}")
    else:
        print_note(f"Run 失败: {err[:200]}")

    # 查看镜像大小
    ret, out, _ = run_docker(["images", tag, "--format", "{{.Size}}"])
    if ret == 0 and out.strip():
        print(f"  {Color.HIGHLIGHT}镜像大小: {out.strip()}{Color.RESET}")

    # 清理
    run_docker(["rmi", "-f", tag])
    import shutil; shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    print_section("s28-08: Agent 容器化实战")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("Agent 容器化 = Dockerfile + Compose + .env")
    print_key_point("API Key 用环境变量注入, 不进镜像!")
