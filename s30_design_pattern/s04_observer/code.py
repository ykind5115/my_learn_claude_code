#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s30-04: 观察者模式"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_note, print_key_point, print_section, print_agent_link

def demo_all():
    print_step(1, "EventBus — 发布订阅")
    class EventBus:
        def __init__(self):
            self._handlers = {}
        def on(self, event, handler):
            self._handlers.setdefault(event, []).append(handler)
        def emit(self, event, data=None):
            print(f"  [Event: {event}]")
            for h in self._handlers.get(event, []):
                h(data)

    bus = EventBus()
    def on_order(data):
        print(f"    库存: 扣减 {data}")
    def on_logistics(data):
        print(f"    物流: 准备发货 {data}")
    def on_notify(data):
        print(f"    通知: 订单 {data} 已确认")

    bus.on("order_created", on_order)
    bus.on("order_created", on_logistics)
    bus.on("order_created", on_notify)
    bus.emit("order_created", "#12345")

    print_agent_link("Observer", "s04 Hooks", "事件触发 -> 回调执行")

if __name__ == "__main__":
    print_section("s30-04: 观察者模式")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("观察者 = EventBus.on + emit")
