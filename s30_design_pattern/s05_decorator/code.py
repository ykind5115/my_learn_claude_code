#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s30-05: 装饰器模式"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_note, print_key_point, print_section, print_agent_link

def demo_all():
    print_step(1, "@timer — 计时装饰器")
    def timer(func):
        def wrapper(*a, **kw):
            start = time.time()
            r = func(*a, **kw)
            elapsed = (time.time() - start) * 1000
            print(f"    耗时: {elapsed:.2f}ms")
            return r
        return wrapper

    @timer
    def slow_add(n):
        return sum(range(n))

    slow_add(100000)

    print_step(2, "@retry — 重试装饰器")
    def retry(max_tries=3):
        def decorator(func):
            def wrapper(*a, **kw):
                for i in range(max_tries):
                    try: return func(*a, **kw)
                    except Exception as e:
                        if i == max_tries - 1: raise
                        print(f"    重试 {i+1}/{max_tries}: {e}")
            return wrapper
        return decorator

    attempts = []
    @retry(max_tries=3)
    def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise Exception("临时错误")
        return "成功!"

    print(f"  {flaky()}")

    print_agent_link("Decorator", "s02 @tool", "@tool 把函数注册为 Agent 工具")

if __name__ == "__main__":
    print_section("s30-05: 装饰器模式")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("装饰器 = 不修改原函数 + 加功能")
