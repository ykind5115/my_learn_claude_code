#!/usr/bin/env python3
"""s31-06: 主从复制"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_key_point, print_section

class ReplicaDB:
    def __init__(self, name):
        self.name = name; self.data = {}
    def write(self, k, v):
        self.data[k] = v
    def read(self, k):
        return self.data.get(k)

class Master(ReplicaDB):
    def __init__(self):
        super().__init__("master"); self.replicas = []
    def add_replica(self, r):
        self.replicas.append(r)
    def write(self, k, v):
        super().write(k, v)
        for r in self.replicas:
            r.data[k] = v  # 同步到从库
        return f"写入 {k}={v} (已同步 {len(self.replicas)} 个从库)"

def demo_all():
    print_step(1, "主从架构")
    master = Master()
    replica1 = ReplicaDB("replica-1")
    replica2 = ReplicaDB("replica-2")
    master.add_replica(replica1); master.add_replica(replica2)

    master.write("user:1", "Alice")
    master.write("user:2", "Bob")

    print(f"  主库: {dict(master.data)}")
    print(f"  从库1: {dict(replica1.data)}")
    print(f"  从库2: {dict(replica2.data)}")

    print_step(2, "读写分离")
    print(f"  写 -> 主库 (master.write)")
    print(f"  读 -> 从库 (replica.read) 分担压力")

    print_step(3, "故障切换")
    print(f"  主库挂了 -> 选举从库1为新主库 -> 继续服务")

if __name__ == "__main__":
    print_section("s31-06: 主从复制")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("主写从读 + 同步 + 故障切换")
