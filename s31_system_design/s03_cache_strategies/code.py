#!/usr/bin/env python3
"""s31-03: 缓存策略"""
import os, sys, time
from collections import OrderedDict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_section

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity; self.cache = OrderedDict()
    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    def put(self, key, val):
        if key in self.cache: self.cache.move_to_end(key)
        self.cache[key] = val
        if len(self.cache) > self.cap: self.cache.popitem(last=False)

class TTLCache:
    def __init__(self, ttl):
        self.ttl = ttl; self.cache = {}
    def get(self, key):
        if key in self.cache:
            val, ts = self.cache[key]
            if time.time() - ts < self.ttl: return val
            del self.cache[key]

def demo_all():
    print_step(1, "LRU Cache")
    lru = LRUCache(3)
    for k, v in [("a",1),("b",2),("c",3)]: lru.put(k,v)
    lru.get("a"); lru.put("d", 4)  # b 最久没用 -> 淘汰
    print(f"  keys: {list(lru.cache.keys())} (b 被淘汰)")

    print_step(2, "TTL Cache")
    ttl = TTLCache(0.1)
    ttl.cache["x"] = (1, time.time())
    print(f"  x={ttl.get('x')} (未过期)")
    time.sleep(0.15)
    print(f"  x={ttl.get('x')} (已过期)")

    print_step(3, "Agent 中的应用")
    print(f"  Prompt caching: system prompt 缓存 -> 省钱+加速")
    print(f"  工具结果缓存: 相同参数直接返回缓存结果")

if __name__ == "__main__":
    print_section("s31-03: 缓存策略")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("LRU=淘汰最久未用 TTL=过期删除")
