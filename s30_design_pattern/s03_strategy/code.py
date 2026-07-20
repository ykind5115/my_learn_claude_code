#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s30-03: 策略模式"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_note, print_key_point, print_section, print_agent_link

def demo_all():
    print_step(1, "策略模式: 支付方式切换")
    from abc import ABC, abstractmethod
    class PaymentStrategy(ABC):
        @abstractmethod
        def pay(self, amount): pass

    class CreditCard(PaymentStrategy):
        def pay(self, amount):
            return f"信用卡支付 {amount} 元 (手续费 1%)"
    class WeChat(PaymentStrategy):
        def pay(self, amount):
            return f"微信支付 {amount} 元 (免手续费)"

    class PaymentContext:
        def __init__(self, strategy: PaymentStrategy):
            self.strategy = strategy
        def set_strategy(self, s): self.strategy = s
        def pay(self, amount): return self.strategy.pay(amount)

    ctx = PaymentContext(CreditCard())
    print(f"  {ctx.pay(100)}")
    ctx.set_strategy(WeChat())
    print(f"  {ctx.pay(100)}")

    print_agent_link("Strategy", "s08 Context Compact", "运行时切换压缩策略")

if __name__ == "__main__":
    print_section("s30-03: 策略模式")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("策略 = 接口统一 + 运行时注入不同实现")
