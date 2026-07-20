#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s30-02: 工厂模式"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_note, print_key_point, print_section, print_agent_link

def demo_all():
    print_step(1, "简单工厂")
    class Dog: pass
    class Cat: pass
    def animal_factory(kind):
        if kind == "dog": return Dog()
        if kind == "cat": return Cat()
    print(f"  animal_factory('dog') = {type(animal_factory('dog')).__name__}")

    print_step(2, "注册式工厂 (Agent 同款)")
    class ToolFactory:
        _tools = {}
        @classmethod
        def register(cls, name, tool_cls):
            cls._tools[name] = tool_cls
        @classmethod
        def create(cls, name):
            return cls._tools.get(name, lambda: None)()

    class BashTool: pass
    class ReadTool: pass
    ToolFactory.register("bash", BashTool)
    ToolFactory.register("read", ReadTool)
    t1 = ToolFactory.create("bash")
    t2 = ToolFactory.create("read")
    print(f"  create('bash') = {type(t1).__name__}")
    print(f"  create('read') = {type(t2).__name__}")

    print_agent_link("Factory", "s02 Tool Use", "tool_use.name -> ToolFactory.create(name)")

if __name__ == "__main__":
    print_section("s30-02: 工厂模式")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("工厂 = 集中管理对象创建 + 按名分发")
