#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s02: Mini Browser — 栈

运行: python s24_data_structures/s02_mini_browser/code.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (
    Color, print_header, print_step, print_note, print_key_point, print_success,
)
from s02_mini_browser.stack import Stack, LinkedListStack
from s02_mini_browser.mini_browser import DemoBrowser


def demo_stack():
    """演示栈的基本操作"""
    print_step(1, "栈的基本操作 — LIFO")

    s = Stack()
    for item in ["A", "B", "C", "D"]:
        s.push(item)
        print_note(f"push('{item}')")

    s.print_structure()

    print_note("pop 操作 (LIFO — 后进先出):")
    while not s.is_empty():
        print_note(f"  pop() → '{s.pop()}'")

    print_key_point(
        "栈 = 只能在一端操作的受限数据结构。\n"
        "    后进先出 (LIFO) —— 最后放进去的最先拿出来。\n"
        "    就像浏览器的后退：你只能回到「上一个」页面。"
    )


def demo_two_stack_browser():
    """演示双栈实现浏览器前进后退"""
    print_step(2, "双栈实现浏览器前进/后退")

    browser = DemoBrowser()

    print_note("用户浏览了一串页面...")
    browser.visit("https://google.com")
    browser.visit("https://github.com")
    browser.visit("https://stackoverflow.com")
    browser.status()

    print_step(3, "后退 → 回到上一个页面")
    browser.back()
    browser.status()

    print_step(4, "再后退")
    browser.back()
    browser.status()

    print_step(5, "前进")
    browser.forward()
    browser.status()

    print_step(6, "后退后又访问新页面 → 前进栈被清空")
    browser.back()
    browser.visit("https://news.ycombinator.com")
    browser.status()
    print_note("注意: 前进栈空了——「后退后访问新页面」让旧的前进历史失效了。")

    print_key_point(
        "浏览器的前进/后退 = 两个栈的协作\n"
        "    后退 = 从 back_stack pop → push 到 forward_stack\n"
        "    前进 = 从 forward_stack pop → push 到 back_stack\n"
        "    访问新页面 = push 到 back_stack + 清空 forward_stack"
    )


def demo_call_stack():
    """演示函数调用栈"""
    print_step(7, "函数调用栈 — Python 运行时也在用栈")

    print_note("当你写递归函数时，Python 用调用栈来管理:")
    print_note("")
    print_note("  def factorial(n):")
    print_note("      if n <= 1: return 1")
    print_note("      return n * factorial(n - 1)")
    print_note("")
    print_note("  factorial(4) → factorial(3) → factorial(2) → factorial(1)")
    print_note("  调用栈:      [f(4)]  →  [f(4),f(3)]  →  [f(4),f(3),f(2)]  → ...")
    print_note("  返回时:      从栈顶逐个弹出并计算结果")
    print_key_point("每一次函数调用 = push，每一次 return = pop。")


def main():
    print_header("s02: Mini Browser — 栈")

    print(f"""
  {Color.HIGHLIGHT}本章的数据结构: 栈 (Stack){Color.RESET}

    {Color.DIM}操作{Color.RESET}    push O(1) / pop O(1) / peek O(1)
    {Color.DIM}核心{Color.RESET}    LIFO — Last In, First Out
    {Color.DIM}应用{Color.RESET}    浏览器前进后退、函数调用栈、撤销(Ctrl+Z)
""")

    demo_stack()
    demo_two_stack_browser()
    demo_call_stack()

    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"\n{Color.SUCCESS}✅ 栈 = 最简单的受限数据结构，LIFO 是它的灵魂{Color.RESET}")
    print(f"{Color.HIGHLIGHT}下一步: 打开 mini_browser.py，实现 TODO 方法！{Color.RESET}\n")


if __name__ == "__main__":
    main()
