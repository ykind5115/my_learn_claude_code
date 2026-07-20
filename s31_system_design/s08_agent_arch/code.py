#!/usr/bin/env python3
"""s31-08: Agent 系统架构"""
import os, sys, random, time
from collections import deque
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_section

class RateLimiter:
    def __init__(self, rate):
        self.rate = rate; self.tokens = rate; self.last = time.time()
    def allow(self):
        now = time.time()
        self.tokens = min(self.rate, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= 1: self.tokens -= 1; return True
        return False

class AgentInstance:
    def __init__(self, name):
        self.name = name; self.cache = {}
    def handle(self, query):
        if query in self.cache:
            return f"{self.name}: [cache] {self.cache[query]}"
        result = f"response_to_{query}"
        self.cache[query] = result
        return f"{self.name}: {result}"

class LoadBalancer:
    def __init__(self, agents):
        self.agents = agents; self.idx = 0
    def route(self, query):
        agent = self.agents[self.idx]
        self.idx = (self.idx + 1) % len(self.agents)
        return agent.handle(query)

def demo_all():
    print_step(1, "Agent 集群架构")
    agents = [AgentInstance(f"agent-{i}") for i in range(3)]
    lb = LoadBalancer(agents)
    limiter = RateLimiter(rate=5)

    queries = ["hello", "world", "hello", "test", "world"]
    for q in queries:
        if limiter.allow():
            print(f"  {lb.route(q)}")
        else:
            print(f"  {Color.ERROR}429 Rate Limited{Color.RESET}")

    print_step(2, "架构要点回顾")
    print(f"  负载均衡 (s02): 轮询分配请求到 3 个 Agent")
    print(f"  缓存 (s03): agent-0 第二次查 'hello' 用缓存")
    print(f"  限流 (s05): 超过 5 req/s 返回 429")
    print(f"  CAP (s07): Agent 集群选 AP (优先可用)")

if __name__ == "__main__":
    print_section("s31-08: Agent 系统架构")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("Agent 架构 = 负载均衡 + 缓存 + 限流 + 消息队列 + CAP 权衡")
