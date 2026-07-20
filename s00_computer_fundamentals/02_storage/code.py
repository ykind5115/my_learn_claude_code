#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s00-02: 磁盘、虚拟内存、文件系统 — 持久化，inode，路径安全

学习目标:
  - 理解磁盘 I/O 的延迟
  - 认识 flush/fsync 的作用
  - 了解 inode 和文件描述符
  - 理解路径遍历攻击

运行: python 02_storage/code.py
"""

import os
import sys
import time
import tempfile


# ═══════════════════════════════════════════════════════════
# Demo 1: 文件 I/O — 写入、缓冲、持久化
# ═══════════════════════════════════════════════════════════
def demo_1_file_io():
    print("── Demo 1: 文件写入与缓冲 ──")

    tmpfile = os.path.join(tempfile.gettempdir(), "s00_demo.txt")

    # 普通写入（可能在页缓存里）
    with open(tmpfile, "w") as f:
        f.write("hello")
        # 此时数据可能还在内存的页缓存，没落到磁盘
        print(f"  write('hello') → 数据可能还在 OS 页缓存")

    # 显式刷盘
    with open(tmpfile, "w") as f:
        f.write("hello")
        f.flush()               # 刷到 OS 缓冲区
        os.fsync(f.fileno())    # 强制写到磁盘
        print(f"  write + flush + fsync → 数据已落盘 ✓")

    # 查看文件 inode 信息
    stat = os.stat(tmpfile)
    print()
    print(f"  文件信息 (os.stat):")
    print(f"    inode: {stat.st_ino}")
    print(f"    大小: {stat.st_size} bytes")
    print(f"    权限: {oct(stat.st_mode)}")
    print(f"    链接数: {stat.st_nlink} (硬链接数)")

    os.remove(tmpfile)
    print()


# ═══════════════════════════════════════════════════════════
# Demo 2: 文件描述符 — 整数代表打开的文件
# ═══════════════════════════════════════════════════════════
def demo_2_file_descriptors():
    print("── Demo 2: 文件描述符 (fd) ──")

    # 打开文件，拿到 fd
    tmpfile = os.path.join(tempfile.gettempdir(), "s00_demo_fd.txt")
    with open(tmpfile, "w") as f:
        fd = f.fileno()
        print(f"  open('{tmpfile}', 'w')")
        print(f"  fileno() = {fd}")
        print(f"  → fd 0=stdin, 1=stdout, 2=stderr. 普通文件从 3 开始")

    # 直接用 os 模块操作 fd
    fd = os.open(tmpfile, os.O_RDONLY)
    print(f"  os.open(只读) → fd = {fd}")
    data = os.read(fd, 100)
    print(f"  os.read({fd}, 100) → {data!r}")
    os.close(fd)
    print(f"  os.close({fd})")

    os.remove(tmpfile)
    print()


# ═══════════════════════════════════════════════════════════
# Demo 3: 路径操作 — 绝对、相对、规范化
# ═══════════════════════════════════════════════════════════
def demo_3_path_operations():
    print("── Demo 3: 路径操作 ──")

    # 各种路径
    print(f"  当前文件: {__file__}")
    print(f"  绝对路径: {os.path.abspath('.')}")
    print(f"  真实路径: {os.path.realpath('.')}")

    # 路径拼接
    project = os.path.abspath(".")
    s01 = os.path.join(project, "s01_agent_loop", "code.py")
    print(f"  os.path.join: {s01}")

    # 解析 ..
    tricky = os.path.abspath(os.path.join(project, "../../etc/passwd"))
    print(f"  os.path.abspath('../' + '../../etc/passwd')")
    print(f"    结果: {tricky}")
    print(f"    → 这就是路径遍历攻击的原理：.. 可以跳出项目目录")

    # 安全检查
    def is_safe(base_dir, target):
        """检查 target 是否在 base_dir 内部"""
        real_base = os.path.realpath(base_dir)
        real_target = os.path.realpath(target)
        safe = real_target.startswith(real_base + os.sep)
        return safe

    safe_path = os.path.join(project, "s01_agent_loop", "code.py")
    unsafe_path = os.path.join(project, "../../etc/passwd")

    print(f"  安全检查:")
    print(f"    s01/code.py 安全? → {is_safe(project, safe_path)} ✓")
    print(f"    ../../etc/passwd 安全? → {is_safe(project, unsafe_path)} ✗")
    print(f"    → s03 权限系统就是用类似方法防止越权访问")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 4: 磁盘 vs 内存速度对比
# ═══════════════════════════════════════════════════════════
def demo_4_disk_vs_memory():
    print("── Demo 4: 磁盘 vs 内存速度 ──")

    # 内存写入
    data_size = 1_000_000
    start = time.time()
    mem_list = [0] * data_size
    mem_time = time.time() - start
    print(f"  内存: 分配 {data_size} 个整数 → {mem_time:.6f}s")

    # 磁盘写入
    tmpfile = os.path.join(tempfile.gettempdir(), "s00_speed_test.bin")
    data = b"x" * data_size
    start = time.time()
    with open(tmpfile, "wb") as f:
        f.write(data)
    disk_time = time.time() - start
    print(f"  磁盘: 写入 {data_size} bytes → {disk_time:.4f}s")
    if mem_time > 0:
        print(f"  磁盘比内存慢约: {disk_time / mem_time:.0f}x")

    os.remove(tmpfile)
    print()


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("s00-02: 磁盘、虚拟内存、文件系统")
    print("=" * 60)
    print()

    demo_1_file_io()
    demo_2_file_descriptors()
    demo_3_path_operations()
    demo_4_disk_vs_memory()

    print("─" * 60)
    print("小结:")
    print("  磁盘 I/O: 比内存慢 1000-100000 倍")
    print("  flush + fsync: 确保数据真正落盘")
    print("  fd (文件描述符): 0=stdin 1=stdout 2=stderr 3+=文件")
    print("  路径安全: os.path.realpath 解析 .. 防止遍历攻击")
