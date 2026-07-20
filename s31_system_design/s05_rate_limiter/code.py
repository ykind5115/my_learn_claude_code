#!/usr/bin/env python3
"""s31-05: 限流"""
import os, sys, time
from collections import deque
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_section

class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate; self.cap = capacity; self.tokens = capacity; self.last = time.time()
    def allow(self):
        now = time.time()
        self.tokens = min(self.cap, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1; return True
        return False

class SlidingWindow:
    def __init__(self, limit, window):
        self.limit = limit; self.window = window; self.requests = deque()
    def allow(self):
        now = time.time()
        while self.requests and now - self.requests[0] > self.window:
            self.requests.popleft()
        if len(self.requests) < self.limit:
            self.requests.append(now); return True
        return False

def demo_all():
    print_step(1, "令牌桶")
    tb = TokenBucket(rate=5, capacity=5)
    result = [tb.allow() for _ in range(6)]
    print(f"  5 token 容量, 请求 6 次: {result} (第 6 次被拒绝)")

    print_step(2, "滑动窗口")
    sw = SlidingWindow(limit=3, window=0.5)
    print(f"  前 3 个: {[sw.allow() for _ in range(3)]}")
    print(f"  第 4 个: {[sw.allow() for _ in range(1)]} (窗口满)")
    time.sleep(0.6)
    print(f"  等 0.6s 后: {[sw.allow() for _ in range(1)]} (窗口滑动了)")

    print_step(3, "Agent 中的应用 (s11)")
    print(f"  API 429 Rate Limited -> 等一会重试")
    print(f"  自己实现限流: 保护不被 API 封禁")

if __name__ == "__main__":
    print_section("s31-05: 限流")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("令牌桶=匀速放令牌 滑动窗口=统计最近W秒")
