#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s30-01: 单例模式"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_note, print_key_point, print_section, print_agent_link

def demo_all():
    print_step(1, "方式1: __new__ 控制")
    class SingletonNew:
        _instance = None
        def __new__(cls):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.data = []
            return cls._instance
    a = SingletonNew(); a.data.append(1)
    b = SingletonNew(); b.data.append(2)
    print(f"  a is b: {a is b}, data={a.data}")

    print_step(2, "方式2: 模块级单例 (Python 最自然)")
    class Config: pass
    config_instance = Config()  # 模块顶层创建
    c1 = config_instance; c2 = config_instance
    print(f"  c1 is c2: {c1 is c2} (import 自动唯一)")

    print_step(3, "方式3: 装饰器单例")
    def singleton(cls):
        inst = {}
        def get(*a, **kw):
            if cls not in inst:
                inst[cls] = cls(*a, **kw)
            return inst[cls]
        return get
    @singleton
    class DB: pass
    d1 = DB(); d2 = DB()
    print(f"  d1 is d2: {d1 is d2}")

    print_agent_link("Singleton", "s09 Memory", "全局唯一 Memory 实例")

if __name__ == "__main__":
    print_section("s30-01: 单例模式")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("单例 = 全局只有一个实例")
