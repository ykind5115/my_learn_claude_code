#!/usr/bin/env python3
"""s31-02: 负载均衡"""
import os, sys, random
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_section

def demo_all():
    servers = ["S1", "S2", "S3"]
    N = 1000

    print_step(1, "轮询 (Round Robin)")
    rr = Counter(); idx = 0
    for i in range(N):
        rr[servers[idx]] += 1; idx = (idx + 1) % len(servers)
    for s in servers: print(f"  {s}: {rr[s]}")

    print_step(2, "随机 (Random)")
    rd = Counter()
    for _ in range(N):
        rd[random.choice(servers)] += 1
    for s in servers: print(f"  {s}: {rd[s]}")

    print_step(3, "加权 (Weighted)")
    weights = {"S1": 5, "S2": 3, "S3": 2}
    pool = [s for s, w in weights.items() for _ in range(w)]
    wd = Counter()
    for _ in range(N):
        wd[random.choice(pool)] += 1
    for s in servers: print(f"  {s}: {wd[s]} (权重 {weights[s]})")

if __name__ == "__main__":
    print_section("s31-02: 负载均衡")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("轮询=均匀, 随机=趋近均匀, 加权=能力强多干活")
