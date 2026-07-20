#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s26-09: 包管理 — apt, pip, venv, 依赖

学习目标:
  - 理解 apt vs pip 的区别
  - 理解虚拟环境的作用
  - 理解依赖和版本锁定

运行: python s26_linux/s09_package_mgmt/code.py
"""

import os
import sys
import subprocess
import importlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (Color, print_step, print_note,
                   print_key_point, print_section)


# ═══════════════════════════════════════════════════════════
def demo_1_pip_list():
    print_step(1, "pip — 查看已安装的 Python 包")
    r = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=columns"],
        capture_output=True, text=True,
    )
    lines = r.stdout.strip().split("\n")
    print(f"  已安装 {len(lines) - 2} 个包 (前 10 个):")
    for line in lines[:11]:
        print(f"    {line}")

    # 查看某个包的版本
    try:
        import anthropic
        print(f"\n  anthropic 版本: {anthropic.__version__}")
    except ImportError:
        pass


def demo_2_apt_info():
    print_step(2, "apt — 系统包管理 (仅 Linux)")
    if sys.platform == "win32":
        print_note("(Windows — apt 不可用，展示概念)")
        print(f"  apt update          → 更新软件源列表")
        print(f"  apt install nginx   → 安装 nginx")
        print(f"  apt search python   → 搜索 python 相关包")
        print(f"  apt list --installed→ 查看已安装")
        print(f"  apt remove nginx    → 卸载 (保留配置)")
        print(f"  apt purge nginx     → 卸载 (连配置一起删)")
    else:
        ret, out, err = subprocess.run(
            ["apt", "list", "--installed"],
            capture_output=True, text=True,
        )
        if ret == 0:
            lines = out.strip().split("\n")
            print(f"  已安装 {len(lines)} 个系统包")


def demo_3_version_locking():
    print_step(3, "版本锁定")
    print(f"  pip 版本锁定:")
    print(f"    requirements.txt:")
    print(f"      anthropic==0.39.0   ← 精确版本")
    print(f"      fastapi>=0.100.0    ← 最低版本")
    print(f"      requests~=2.31.0    ← 兼容版本 (2.31.x)")

    print(f"\n  {Color.HIGHLIGHT}锁定版本的重要性:{Color.RESET}")
    print(f"    → 确保所有环境安装相同的包版本")
    print(f"    → 避免 '在我的机器上能跑' 问题")
    print(f"    → pip freeze > requirements.txt 导出当前版本")
    print_key_point("项目的 requirements.txt 就是这么生成的")


def demo_4_venv():
    print_step(4, "虚拟环境 (venv)")

    print(f"  Python 虚拟环境:")
    print(f"    $ python -m venv myenv")
    print(f"    $ source myenv/bin/activate   (Linux/macOS)")
    print(f"    $ myenv\\Scripts\\activate      (Windows)")
    print(f"    (myenv) $ pip install xxx     ← 只装在这个环境里")
    print(f"    (myenv) $ deactivate          ← 退出")

    print(f"\n  {Color.HIGHLIGHT}为什么要用虚拟环境?{Color.RESET}")
    print(f"    → 项目 A 需要 numpy==1.24")
    print(f"    → 项目 B 需要 numpy==2.0")
    print(f"    → 全局装一个版本 → 冲突!")
    print(f"    → 每个项目自己的 venv → 各装各的，互不影响")

    # 检查当前是否在虚拟环境中
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print(f"\n  {Color.SUCCESS}✓ 当前在虚拟环境中{Color.RESET}")
        print(f"    prefix: {sys.prefix}")
    else:
        print(f"\n  {Color.WARNING}(当前不在虚拟环境中){Color.RESET}")
        print_note(f"  当前 Python: {sys.executable}")


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_section("s26-09: 包管理")

    demo_1_pip_list()
    demo_2_apt_info()
    demo_3_version_locking()
    demo_4_venv()

    print(f"\n{Color.BOLD}{'─'*60}{Color.RESET}")
    print_key_point("小结:")
    print_key_point("  apt 管系统软件, pip 管 Python 库")
    print_key_point("  requirements.txt 锁定版本 (==, >=, ~=)")
    print_key_point("  venv 虚拟环境 = 每个项目独立的包空间")
