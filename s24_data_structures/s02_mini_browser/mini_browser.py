#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini Browser — 用双栈实现前进/后退

浏览器的「后退」和「前进」按钮是最经典的栈应用。

═══════════════════════════════════════════════════════════════
核心思想: 用两个栈

   后退栈 (back_stack)     前进栈 (forward_stack)
   ┌────────────┐         ┌────────────┐
   │ 购物车      │         │            │
   │ 商品详情    │         │            │
   │ 搜索页      │         │            │
   │ 首页        │         │            │
   └────────────┘         └────────────┘

   - 访问新页面: push 到后退栈，清空前进栈
   - 后退: 从后退栈 pop → push 到前进栈
   - 前进: 从前进栈 pop → push 到后退栈

═══════════════════════════════════════════════════════════════
你的任务: 实现 Browser 类中标记为 TODO 的方法
"""

import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from s02_mini_browser.stack import Stack


class Browser:
    """迷你浏览器 — 支持前进/后退"""

    def __init__(self):
        self.back_stack = Stack()     # 后退历史
        self.forward_stack = Stack()  # 前进历史
        self.current_page = None      # 当前页面

    def visit(self, url):
        """
        访问一个新页面。

        操作:
          1. 如果当前页面存在，把它 push 到后退栈
          2. 前进栈清空 (为什么？因为「后退后再访问新页面」，旧的前进历史没用了)
          3. 设置当前页面 = url
        """
        # TODO: 实现 visit
        #
        # 提示:
        #   if self.current_page is not None:
        #       self.back_stack.push(self.current_page)
        #   while not self.forward_stack.is_empty():
        #       self.forward_stack.pop()  # 清空前进栈
        #   self.current_page = url
        #
        raise NotImplementedError("TODO: 实现 visit")

    def back(self):
        """
        后退 — 回到上一个页面。

        操作:
          1. 如果后退栈为空，返回 None (没有更早的页面了)
          2. 当前页面 push 到前进栈
          3. 从后退栈 pop 一个页面，设为当前页面
          4. 返回新当前页面

        返回: 后退后的页面 URL，或 None
        """
        # TODO: 实现 back
        raise NotImplementedError("TODO: 实现 back")

    def forward(self):
        """
        前进 — 回到刚才「后退掉」的页面。

        操作:
          1. 如果前进栈为空，返回 None
          2. 当前页面 push 到后退栈
          3. 从前进栈 pop 一个页面，设为当前页面
          4. 返回新当前页面

        返回: 前进后的页面 URL，或 None
        """
        # TODO: 实现 forward
        raise NotImplementedError("TODO: 实现 forward")

    # ═══════════════════════════════════════════════════════════
    # 辅助方法 (已实现)
    # ═══════════════════════════════════════════════════════════

    def can_go_back(self):
        return not self.back_stack.is_empty()

    def can_go_forward(self):
        return not self.forward_stack.is_empty()

    def status(self):
        """显示当前状态"""
        print(f"\n  当前页面: {self.current_page or '(无)'}")
        print(f"  后退栈: {len(self.back_stack)} 页  {self.back_stack}")
        print(f"  前进栈: {len(self.forward_stack)} 页  {self.forward_stack}")


class DemoBrowser(Browser):
    """演示用的完整实现 — 学生可以参考但不能直接复制"""

    def visit(self, url):
        if self.current_page is not None:
            self.back_stack.push(self.current_page)
        while not self.forward_stack.is_empty():
            self.forward_stack.pop()
        self.current_page = url
        print(f"    访问: {url}")

    def back(self):
        if self.back_stack.is_empty():
            print("    无法后退")
            return None
        self.forward_stack.push(self.current_page)
        self.current_page = self.back_stack.pop()
        print(f"    后退到: {self.current_page}")
        return self.current_page

    def forward(self):
        if self.forward_stack.is_empty():
            print("    无法前进")
            return None
        self.back_stack.push(self.current_page)
        self.current_page = self.forward_stack.pop()
        print(f"    前进到: {self.current_page}")
        return self.current_page
