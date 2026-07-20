#!/usr/bin/env python3
"""s31-01: 单体 vs 微服务"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_note, print_section

def demo_all():
    print_step(1, "单体架构")
    print(f"  所有功能在一个进程:")
    print(f"    def handle(request):")
    print(f"      if 'auth': return auth(request)")
    print(f"      if 'api': return api(request)")
    print(f"      if 'task': return task(request)")
    print_note("优点: 简单、一键部署。缺点: 耦合")

    print_step(2, "微服务架构")
    print(f"  拆成独立服务:")
    print(f"    auth-service  (port 8001)")
    print(f"    api-service   (port 8002)")
    print(f"    task-service  (port 8003)")
    print(f"  服务间通过 HTTP/gRPC/消息队列通信")
    print_note("优点: 独立扩缩。缺点: 运维复杂")

    print_step(3, "什么时候拆?")
    print(f"  拆: 团队大了、某模块瓶颈、独立部署需求")
    print(f"  不拆: 小团队、早期项目、简单业务")

if __name__ == "__main__":
    print_section("s31-01: 单体 vs 微服务")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("先单体，痛了再拆，不要过早微服务")
