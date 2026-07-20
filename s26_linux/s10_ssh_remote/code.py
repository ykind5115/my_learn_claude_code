#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s26-10: SSH 与远程操作 — 密钥认证, scp, 端口转发

学习目标:
  - 理解 SSH 的工作原理
  - 理解密钥对认证
  - 了解 scp 和端口转发

运行: python s26_linux/s10_ssh_remote/code.py
"""

import os
import sys
import subprocess
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, print_step, print_note,
                   print_key_point, print_section)


# ═══════════════════════════════════════════════════════════
def demo_1_ssh_concept():
    print_step(1, "SSH — 加密的远程 Shell")
    print(f"  SSH = Secure Shell")
    print(f"    两个功能:")
    print(f"      1. 加密 — 你和服务器之间的数据旁人看不到")
    print(f"      2. 认证 — 确认'你就是你'")
    print()
    print(f"  基本用法:")
    print(f"    {Color.COMMAND}ssh user@host{Color.RESET}              → 远程登录")
    print(f"    {Color.COMMAND}ssh user@host 'ls -la'{Color.RESET}    → 在远程执行命令")
    print(f"    {Color.COMMAND}ssh -p 2222 user@host{Color.RESET}     → 指定端口")


def demo_2_key_auth():
    print_step(2, "密钥对认证 — 免密登录")
    print(f"  密码认证:")

    home = Path.home()
    ssh_dir = home / ".ssh"

    print(f"    ssh user@host → 每次都要输密码 ✗")
    print()
    print(f"  密钥认证:")
    print(f"    {Color.COMMAND}ssh-keygen -t rsa{Color.RESET}           → 生成密钥对")

    # 检查本地是否有密钥
    if ssh_dir.exists():
        for key_file in ["id_rsa", "id_ed25519", "id_ecdsa"]:
            if (ssh_dir / key_file).exists():
                print(f"      ✓ 找到私钥: ~/.ssh/{key_file}")
                break
        else:
            print(f"      (未找到私钥 — 需要 ssh-keygen)")
    else:
        print(f"      (没有 ~/.ssh/ 目录 — 需要 ssh-keygen)")

    print(f"    {Color.COMMAND}ssh-copy-id user@host{Color.RESET}      → 上传公钥到服务器")
    print(f"    {Color.COMMAND}ssh user@host{Color.RESET}              → 不用输密码! ✓")
    print()
    print(f"  原理:")
    print(f"    私钥 (你保管) → 签名'我是xxx'")
    print(f"    公钥 (服务器上) → 验证签名 → 通过!")


def demo_3_scp():
    print_step(3, "SCP — 安全拷贝文件")
    print(f"  上传文件到服务器:")
    print(f"    {Color.COMMAND}scp file.txt user@host:/remote/path/{Color.RESET}")
    print(f"  从服务器下载文件:")
    print(f"    {Color.COMMAND}scp user@host:/remote/file.txt ./local/{Color.RESET}")
    print(f"  递归拷贝目录:")
    print(f"    {Color.COMMAND}scp -r project/ user@host:/remote/{Color.RESET}")


def demo_4_port_forward():
    print_step(4, "端口转发 — 把远程端口'搬'到本地")
    print(f"  场景: 远程服务器的 PostgreSQL 只监听 localhost:5432")
    print(f"  你想在本机连接它:")
    print(f"    {Color.COMMAND}ssh -L 5432:localhost:5432 user@host{Color.RESET}")
    print(f"    → 本地的 5432 端口 → 隧道 → 远程的 5432 端口")
    print(f"    → python 连接 localhost:5432 = 连接远程 PostgreSQL!")


def demo_5_agent_relevance():
    print_step(5, "跟 Agent 的关系")
    print(f"  s19 MCP:")
    print(f"    → 远程 Agent 通信可以用 SSH 隧道加密")
    print(f"  Agent 自动化:")
    print(f"    → 免密登录让 Agent 能自动操作远程服务器")
    print(f"    → scp 自动部署代码 / 收集日志")
    print(f"    → 端口转发让本地工具访问远程服务")


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_section("s26-10: SSH 与远程操作")

    demo_1_ssh_concept()
    demo_2_key_auth()
    demo_3_scp()
    demo_4_port_forward()
    demo_5_agent_relevance()

    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("小结:")
    print_key_point("  ssh = 加密 + 认证 (密码 或 密钥)")
    print_key_point("  ssh-keygen + ssh-copy-id → 免密登录")
    print_key_point("  scp = 安全拷贝文件 (上传/下载)")
    print_key_point("  ssh -L = 端口转发 (把远程端口搬到你本地)")
