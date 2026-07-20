#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s30-06: 适配器模式"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_note, print_key_point, print_section, print_agent_link

def demo_all():
    print_step(1, "问题: 两个不兼容的接口")
    class OldPrinter:
        def print_old(self, text):
            return f"[OLD] {text}"
    class NewPrinter:
        def render(self, text, style="normal"):
            return f"[{style.upper()}] {text}"

    print_step(2, "适配器统一接口")
    from abc import ABC, abstractmethod
    class Printer(ABC):
        @abstractmethod
        def output(self, text): pass

    class OldAdapter(Printer):
        def __init__(self):
            self.old = OldPrinter()
        def output(self, text):
            return self.old.print_old(text)

    class NewAdapter(Printer):
        def __init__(self):
            self.new = NewPrinter()
        def output(self, text):
            return self.new.render(text, "fancy")

    # 使用统一接口
    for adapter in [OldAdapter(), NewAdapter()]:
        print(f"  {adapter.output('Hello')}")

    print_agent_link("Adapter", "s19 MCP", "stdio/HTTP/SSE -> 统一 MCP 接口")

if __name__ == "__main__":
    print_section("s30-06: 适配器模式")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("适配器 = 中间层 + 统一接口")
