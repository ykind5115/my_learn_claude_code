#!/usr/bin/env python3
"""s31-07: CAP 定理"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_section

def demo_all():
    print_step(1, "CAP 不可能三角")
    print(f"         Consistency (一致性)")
    print(f"            /\\")
    print(f"           /  \\")
    print(f"          /    \\")
    print(f"         /  CA  \\")
    print(f"        /        \\")
    print(f"  Availability ──────── Partition Tolerance")
    print(f"     (可用性)    AP    (分区容错)")

    print_step(2, "网络分区时的选择")
    print(f"  CP (一致+分区):")
    print(f"    网络断开 -> 拒绝写入 -> 保证数据一致")
    print(f"    适合: 银行转账、订单系统")
    print(f"  AP (可用+分区):")
    print(f"    网络断开 -> 继续接受写入 -> 之后同步")
    print(f"    适合: 社交媒体、博客")

    print_step(3, "Agent 中的应用")
    print(f"  Agent 集群: 选择 AP (优先可用, 允许短暂不一致)")
    print(f"  Memory 系统: 选择 CP (记忆不能错)")

if __name__ == "__main__":
    print_section("s31-07: CAP 定理")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("CAP: 一致性/可用性/分区容错 只能三选二")
