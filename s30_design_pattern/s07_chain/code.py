#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s30-07: 责任链模式"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_note, print_key_point, print_section, print_agent_link

def demo_all():
    print_step(1, "审批链: 组长 -> 经理 -> 总监")
    class Handler:
        def __init__(self, name, max_amount):
            self.name = name
            self.max = max_amount
            self._next = None
        def set_next(self, h):
            self._next = h; return h
        def handle(self, amount):
            if amount <= self.max:
                return f"{self.name} 批准了 {amount} 元"
            elif self._next:
                return self._next.handle(amount)
            return f"金额 {amount} 元 无人能批"

    leader = Handler("组长", 1000)
    manager = Handler("经理", 10000)
    director = Handler("总监", 100000)
    leader.set_next(manager).set_next(director)

    for amt in [500, 5000, 50000, 500000]:
        print(f"  申请 {amt} 元 -> {leader.handle(amt)}")

    print_agent_link("Chain of Responsibility", "s03 Permission", "allow->deny->ask 权限链")

if __name__ == "__main__":
    print_section("s30-07: 责任链")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("责任链 = 请求沿链传递, 每层可处理或传递")
