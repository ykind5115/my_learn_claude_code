#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s12: AOF 日志 — 记录每一次写字

Chapter 4: 持久化 — 别让黑板断电就没了

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - AOF 持久化是怎么工作的？
  - appendfsync 三种策略的区别是什么？
  - AOF 重写（Rewrite）解决了什么问题？
  - RDB + AOF 混合持久化是什么？
  - RDB 和 AOF 什么时候该用哪个？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s12_aof/code.py
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# 确保项目根目录在 sys.path 中，以便导入 utils
_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s25_redis.utils import (
    Color,
    get_redis_client,
    show_blackboard,
    print_step,
    print_command,
    print_note,
    print_key_point,
    print_result,
    section,
    flush_db,
)


def try_read_file(filepath):
    """尝试读取文件内容，不存在的文件返回 None"""
    try:
        with open(filepath, "rb") as f:
            return f.read()
    except (FileNotFoundError, PermissionError, OSError):
        return None


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s12: AOF 日志 — 记录每一次写字{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
  {Color.DIM}上一章我们看到 RDB 会丢数据——两次快照之间写入的数据，断电就没了。

  AOF 不怕：把每次在黑板上写的动作都记在本子上。
  断电后，按本子重做一遍，黑板就恢复原样。

  AOF = Append Only File（追加写文件）
  本子越写越厚——但我们可以「重写」（Rewrite）来压缩它。

  这一章我们来看看 AOF 怎么工作。{Color.RESET}
  """)

    # ────────────────────────────────────────────────────────────
    # 连接 Redis
    # ────────────────────────────────────────────────────────────
    client = get_redis_client()
    print(f"  {Color.SUCCESS}✅ 已连接到 Redis{Color.RESET}\n")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步：查看当前 AOF 配置
    # ═══════════════════════════════════════════════════════════
    print_step(1, "查看当前 AOF 配置")

    appendonly = client.config_get("appendonly")
    appendfsync = client.config_get("appendfsync")
    appendfilename = client.config_get("appendfilename")
    aof_dir = client.config_get("dir")
    auto_aof_rewrite_percentage = client.config_get("auto-aof-rewrite-percentage")
    auto_aof_rewrite_min_size = client.config_get("auto-aof-rewrite-min-size")
    aof_use_rdb_preamble = client.config_get("aof-use-rdb-preamble")

    print_command("CONFIG GET appendonly", "AOF 是否开启")
    print_result(appendonly["appendonly"])
    aof_enabled = appendonly["appendonly"] == "yes"
    if aof_enabled:
        print(f"  {Color.SUCCESS}  AOF 已开启 ✓{Color.RESET}")
    else:
        print(f"  {Color.WARNING}  AOF 未开启，稍后我们将动态开启它{Color.RESET}")

    print()
    print_command("CONFIG GET appendfsync", "AOF fsync 策略")
    print_result(appendfsync["appendfsync"])
    print_note("everysec = 每秒刷一次盘（默认推荐，最多丢 1 秒数据）")

    print()
    print_command("CONFIG GET appendfilename", "AOF 文件名")
    print_result(appendfilename["appendfilename"])

    print()
    print_command('CONFIG GET dir', "AOF 文件保存目录")
    aof_dir_path = aof_dir["dir"]
    print_result(aof_dir_path)

    aof_file_path = os.path.join(aof_dir_path, appendfilename["appendfilename"])
    print(f"  {Color.DIM}AOF 文件完整路径: {aof_file_path}{Color.RESET}")

    print()
    print_command("CONFIG GET auto-aof-rewrite-percentage", "AOF 重写触发百分比")
    print_result(auto_aof_rewrite_percentage["auto-aof-rewrite-percentage"])
    print_note("AOF 文件增长到上次重写大小的 N% 时触发重写（默认 100%）")

    print()
    print_command("CONFIG GET auto-aof-rewrite-min-size", "AOF 重写触发最小大小")
    print_result(auto_aof_rewrite_min_size["auto-aof-rewrite-min-size"])
    print_note("AOF 文件至少达到此大小才触发重写（默认 64 MB，防止小文件频繁重写）")

    print()
    print_command("CONFIG GET aof-use-rdb-preamble", "AOF 混合持久化（RDB + AOF）")
    print_result(aof_use_rdb_preamble["aof-use-rdb-preamble"])
    if aof_use_rdb_preamble["aof-use-rdb-preamble"] == "yes":
        print(f"  {Color.SUCCESS}  ✅ 混合模式已开启——AOF 文件以 RDB 头开头，恢复速度接近 RDB{Color.RESET}")

    print_key_point(
        "AOF 的核心配置:\n"
        "    appendonly yes/no                — 是否开启 AOF\n"
        "    appendfsync always/everysec/no   — 刷盘策略\n"
        "    auto-aof-rewrite-percentage 100  — 文件增长 100% 触发重写\n"
        "    auto-aof-rewrite-min-size 64mb   — 至少 64 MB 才触发重写\n"
        "    aof-use-rdb-preamble yes         — 混合持久化（Redis 4.0+）"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 2 步：如果 AOF 没开启，动态开启
    # ═══════════════════════════════════════════════════════════
    if not aof_enabled:
        print_step(2, "动态开启 AOF（不需要重启 Redis）")

        section("CONFIG SET appendonly yes")
        print(f"  {Color.WARNING}⚠ 正在运行时开启 AOF...{Color.RESET}")
        print_note("CONFIG SET 是热修改，生产环境慎用——首次开启 AOF 会阻塞直到初始 AOF 文件写入完成")

        try:
            client.config_set("appendonly", "yes")
            print(f"  {Color.SUCCESS}✅ AOF 已开启！{Color.RESET}")
        except Exception as e:
            print(f"  {Color.ERROR}❌ 开启失败: {e}{Color.RESET}")
            print(f"  {Color.WARNING}  可能是权限限制，尝试继续演示...{Color.RESET}")

        # 等待 AOF 初始化完成
        time.sleep(1)

    # ═══════════════════════════════════════════════════════════
    # 第 3 步：写入数据并观察 AOF 文件
    # ═══════════════════════════════════════════════════════════
    print_step(3, "写入数据，观察 AOF 文件增长")

    section("写入数据前先检查 AOF 文件状态")
    info = client.info("persistence")
    aof_size_before = info.get("aof_current_size", 0)
    print_command("INFO persistence", "查看 AOF 当前大小")
    print(f"  {Color.DIM}  当前 AOF 文件大小: {Color.RESET}{Color.HIGHLIGHT}{aof_size_before:,}{Color.RESET}{Color.DIM} 字节{Color.RESET}")

    section("写入 5 个 key")
    print_command('SET demo:aof:user "张三"')
    client.set("demo:aof:user", "张三")
    print_command('SET demo:aof:product "手机"')
    client.set("demo:aof:product", "手机")
    print_command('INCR demo:aof:visits')
    client.incr("demo:aof:visits")
    print_command('INCR demo:aof:visits')
    client.incr("demo:aof:visits")
    print_command('INCR demo:aof:visits')
    client.incr("demo:aof:visits")

    print()
    show_blackboard(client, "黑板上写入后的状态", "demo:aof:*")

    # 再次检查 AOF 大小
    info = client.info("persistence")
    aof_size_after = info.get("aof_current_size", 0)
    aof_size_grew = aof_size_after - aof_size_before
    print(f"  {Color.DIM}AOF 文件大小变化: {Color.RESET}"
          f"{aof_size_before:,} → {Color.HIGHLIGHT}{aof_size_after:,}{Color.RESET}"
          f"{Color.DIM} 字节 (+{aof_size_grew} 字节){Color.RESET}")
    print_note("5 条命令在 AOF 文件中对应 5 段 RESP 协议编码的命令")

    print_key_point(
        "AOF 记录的是「写命令」，不是数据本身。\n"
        "    INCR demo:aof:visits 被执行了 3 次 → AOF 中记录了 3 行 INCR。\n"
        "    如果把 AOF 文件拿出来重放，它就会逐条执行这些命令，恢复最终状态。\n"
        "    但这也是 AOF 文件大、恢复慢的原因——3 次 INCR 完全可以压缩成 1 条 SET。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步：查看 AOF 文件内容
    # ═══════════════════════════════════════════════════════════
    print_step(4, "查看 AOF 文件内容")

    section("尝试读取 AOF 文件")

    # 尝试从本地文件系统读取
    raw_content = try_read_file(aof_file_path)

    if raw_content:
        print(f"  {Color.SUCCESS}✅ 成功读取 AOF 文件（{len(raw_content)} 字节）{Color.RESET}")
        print()

        # 将内容按行解码并显示前 30 行
        try:
            text = raw_content.decode("utf-8", errors="replace")
        except Exception:
            text = raw_content.decode("latin-1", errors="replace")

        lines = text.splitlines()
        print(f"  {Color.BOARD}AOF 文件内容预览（前 40 行）：{Color.RESET}")
        print(f"  {Color.BOARD}{'─' * 55}{Color.RESET}")

        # AOF 使用 RESP 协议，每行以 * 开头表示数组，$ 开头表示字符串长度
        # 我们格式化地展示
        display_count = 0
        in_command = False
        cmd_parts = []
        for line in lines[:40]:
            if line.startswith("*"):
                if cmd_parts:
                    print(f"  {Color.YELLOW}{' '.join(cmd_parts)}{Color.RESET}")
                    cmd_parts = []
                # 新命令开始
                in_command = True
                display_count += 1
                print(f"  {Color.CYAN}[命令 {display_count}]{Color.RESET}")
                print(f"    {Color.DIM}{line}{Color.RESET}")
            elif line.startswith("$"):
                print(f"    {Color.DIM}{line}{Color.RESET}")
            else:
                print(f"    {Color.GREEN}{line}{Color.RESET}")

        if cmd_parts:
            print(f"  {Color.YELLOW}{' '.join(cmd_parts)}{Color.RESET}")

        print(f"  {Color.BOARD}{'─' * 55}{Color.RESET}")

        if len(lines) > 40:
            print(f"  {Color.DIM}...（共 {len(lines)} 行，仅显示前 40 行）{Color.RESET}")

        print_note("AOF 使用 RESP 协议：*3 表示数组长度 3（即 SET key value），$3 表示字符串长度 3")
        print_note("所以 INCR counter 在 AOF 中保存为：*2\\r\\n$4\\r\\nINCR\\r\\n$7\\r\\ncounter\\r\\n")
    else:
        # 文件不可读（可能是 Docker 或权限问题）
        print(f"  {Color.WARNING}⚠ 无法直接读取 AOF 文件（可能在 Docker 容器内）{Color.RESET}")
        print(f"     {Color.DIM}路径: {aof_file_path}{Color.RESET}")
        print()
        print(f"  {Color.DIM}AOF 文件包含 RESP 协议格式的写命令，例如：{Color.RESET}")
        print(f"  {Color.DIM}  SET demo:aof:user \"张三\"{Color.RESET}")
        print(f"  {Color.DIM}  → 在 AOF 文件中编码为：{Color.RESET}")
        print(f"  {Color.DIM}     *3\\r\\n$3\\r\\nSET\\r\\n$14\\r\\ndemo:aof:user\\r\\n$6\\r\\n张三\\r\\n{Color.RESET}")
        print()
        print(f"  {Color.DIM}你可以用以下命令在容器内查看 AOF 文件：{Color.RESET}")
        print(f"  {Color.DIM}  docker exec <container> cat {aof_file_path}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步：演示 AOF 为什么需要 Rewrite
    # ═══════════════════════════════════════════════════════════
    print_step(5, "AOF 膨胀原理 — 为什么需要 Rewrite")

    section("重写前的冗余 INCR 命令")

    # 模拟多次 INCR（用循环写）
    print_command("INCR demo:aof:visits × 5（循环 5 次）")
    for _ in range(5):
        client.incr("demo:aof:visits")

    # 再 SET 同一个 key 多次（经典的冗余场景）
    print_command('SET demo:aof:status "created"')
    client.set("demo:aof:status", "created")
    print_command('SET demo:aof:status "paid"')
    client.set("demo:aof:status", "paid")
    print_command('SET demo:aof:status "shipped"')
    client.set("demo:aof:status", "shipped")
    print_command('SET demo:aof:status "delivered"')
    client.set("demo:aof:status", "delivered")

    show_blackboard(client, "多次写入后的黑板状态", "demo:aof:*")

    # 查看 AOF 大小
    info = client.info("persistence")
    aof_current = info.get("aof_current_size", 0)
    aof_expected = info.get("aof_base_size", 0)

    print(f"""
  {Color.WARNING}AOF 文件中实际上记录了：{Color.RESET}
    {Color.DIM}  INCR demo:aof:visits  →  8 次（但最终值只需要 1 行 SET）{Color.RESET}
    {Color.DIM}  SET demo:aof:status  →  4 次（但最终状态只需要 1 行 SET）{Color.RESET}

  {Color.WARNING}问题：{Color.RESET}
    AOF 文件记录了每一步中间状态，而不是最终状态。
    如果什么都不做，AOF 文件会越来越大，恢复也越来越慢。

  {Color.SUCCESS}解决方案：AOF Rewrite（重写）{Color.RESET}
    BGREWRITEAOF 读取内存中的当前数据，生成最精简的 AOF 文件：
      SET demo:aof:visits 8        ← 只有最终值
      SET demo:aof:status delivered  ← 只有最终状态
      ...（每个 key 只有一行）
  """)

    # ═══════════════════════════════════════════════════════════
    # 第 6 步：触发 AOF 重写
    # ═══════════════════════════════════════════════════════════
    print_step(6, "触发 AOF 重写 — 压缩日志文件")

    info = client.info("persistence")
    aof_size_before_rewrite = info.get("aof_current_size", 0)
    aof_base_before = info.get("aof_base_size", 0)

    print(f"  重写前 AOF 文件大小: {Color.HIGHLIGHT}{aof_size_before_rewrite:,}{Color.RESET} 字节")

    section("执行 BGREWRITEAOF")
    print_command("BGREWRITEAOF", "后台触发 AOF 重写（fork 子进程执行）")
    try:
        result = client.execute_command("BGREWRITEAOF")
        print_result(result, "BGREWRITEAOF 返回")
    except Exception as e:
        print(f"  {Color.WARNING}BGREWRITEAOF 返回: {e}{Color.RESET}")
        print_note("如果 Redis 版本较低或配置不支持，可以用 INFO 查看状态")

    # 等待重写完成
    print(f"\n  {Color.DIM}等待 AOF 重写完成...{Color.RESET}")
    time.sleep(2)
    for _ in range(30):
        info = client.info("persistence")
        if info.get("aof_rewrite_in_progress") == 0:
            break
        time.sleep(0.5)

    section("重写后检查 AOF 文件大小")
    info = client.info("persistence")
    aof_size_after_rewrite = info.get("aof_current_size", 0)
    aof_base_after = info.get("aof_base_size", 0)

    shrunk = aof_size_before_rewrite - aof_size_after_rewrite

    print(f"  重写前: {Color.HIGHLIGHT}{aof_size_before_rewrite:,}{Color.RESET} 字节")
    print(f"  重写后: {Color.HIGHLIGHT}{aof_size_after_rewrite:,}{Color.RESET} 字节")

    if shrunk > 0:
        print(f"  压缩了: {Color.SUCCESS}{shrunk:,}{Color.RESET} 字节 ({shrunk / aof_size_before_rewrite * 100:.1f}%)")
    elif aof_size_after_rewrite == aof_size_before_rewrite:
        print(f"  {Color.DIM}大小不变（可能是因为数据量小，重写效果不明显）{Color.RESET}")
    else:
        print(f"  大小略微增加（重写后有 RDB 头部）: {Color.HIGHLIGHT}{aof_size_after_rewrite:,}{Color.RESET} 字节")

    # 查看重写耗时
    rewrite_time = info.get("aof_last_rewrite_time_sec", "N/A")
    rewrite_status = info.get("aof_last_bgrewrite_status", "N/A")
    print(f"\n  {Color.DIM}重写耗时:{Color.RESET} {Color.HIGHLIGHT}{rewrite_time}{Color.RESET}{Color.DIM} 秒{Color.RESET}")
    print(f"  {Color.DIM}重写状态:{Color.RESET} "
          f"{Color.SUCCESS if rewrite_status == 'ok' else Color.WARNING}{rewrite_status}{Color.RESET}")

    # 再次尝试读取 AOF 文件，展示重写后的内容
    if raw_content:
        new_content = try_read_file(aof_file_path)
        if new_content and len(new_content) < len(raw_content) * 1.2:  # 没有显著增大
            print(f"\n  {Color.DIM}重写后的 AOF 文件已被压缩，内容更精简{Color.RESET}")
    else:
        # 尝试再读一次（也许权限变了）
        new_content = try_read_file(aof_file_path)
        if new_content:
            print(f"\n  {Color.SUCCESS}✅ 重写后的 AOF 文件可读取了！{Color.RESET}")

    print_key_point(
        "AOF Rewrite 的核心思想：\n"
        "    「读取当前内存状态，生成最少命令，替换旧日志」\n"
        "    不是修改旧文件，而是 fork 子进程生成新文件，再原子替换。\n"
        "    中间产生的新写入操作被记录在「重写缓冲区」，最后追加到新文件尾部。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 7 步：三种 fsync 策略对比
    # ═══════════════════════════════════════════════════════════
    print_step(7, "三种 appendfsync 策略对比")

    section("fsync 是什么？")
    print(f"""
  {Color.DIM}当 Redis 执行 SET key value 时，AOF 写入流程：{Color.RESET}

  ① Redis 执行命令，更新内存中的值
  ② Redis 调用 write() 将命令写入 AOF 文件的系统缓冲区（Page Cache）
     → 此时数据还在内存中，没有真正写入硬盘
  ③ Redis 调用 fsync() 将缓冲区数据强制刷入硬盘
     → 此时数据才真正落在硬盘上，断电也不会丢

  {Color.WARNING}write() 很快，但断电可能丢数据（数据在系统缓冲区）{Color.RESET}
  {Color.SUCCESS}fsync() 慢但安全（数据已写入硬盘）{Color.RESET}
  """)

    section("三种策略对比")
    print(f"""
  ┌──────────────┬────────────────────────────────────────────────┬──────────────────────┐
  │  策略         │  行为                                          │  数据丢失窗口          │
  ├──────────────┼────────────────────────────────────────────────┼──────────────────────┤
  │  always      │  每个写命令后都 fsync                           │  最多 1 个命令        │
  │               │  → 最安全，但磁盘 IO 密集，吞吐量低              │                      │
  ├──────────────┼────────────────────────────────────────────────┼──────────────────────┤
  │  everysec    │  每秒钟 fsync 一次                              │  最多 1 秒的数据      │
  │               │  → 默认推荐，兼顾安全与性能                      │                      │
  ├──────────────┼────────────────────────────────────────────────┼──────────────────────┤
  │  no          │  不主动 fsync，由操作系统决定                    │  可能几十秒的数据      │
  │               │  → 最快，但最不安全                             │                      │
  └──────────────┴────────────────────────────────────────────────┴──────────────────────┘
  """)

    section("性能测试对比")
    print(f"""
  {Color.DIM}下面的数据展示不同 fsync 策略对写入性能的影响：{Color.RESET}

  {Color.HIGHLIGHT}appendfsync always:{Color.RESET}
    每个写命令都要 fsync 一次磁盘 → 约 1,000 ~ 2,000 ops/sec
    适合：金融交易、支付流水（不能丢数据）

  {Color.HIGHLIGHT}appendfsync everysec:{Color.RESET}
    每秒 fsync 一次 → 约 10,000 ~ 50,000+ ops/sec
    适合：绝大多数场景（默认推荐）

  {Color.HIGHLIGHT}appendfsync no:{Color.RESET}
    不主动 fsync → 可达到纯内存性能 ~100,000+ ops/sec
    适合：纯缓存场景（丢了可以从 DB 恢复）

  {Color.DIM}（以上为机械硬盘的大概数据，SSD 会快很多）{Color.RESET}
  """)

    # 显示当前配置
    print_command("CONFIG GET appendfsync", "当前 fsync 策略")
    current_fsync = client.config_get("appendfsync")["appendfsync"]
    print_result(current_fsync)

    # ═══════════════════════════════════════════════════════════
    # 第 8 步：查看 AOF 持久化完整状态
    # ═══════════════════════════════════════════════════════════
    print_step(8, "查看 AOF 持久化完整状态")

    section("INFO persistence — AOF 相关指标")
    info = client.info("persistence")
    aof_fields = [
        ("aof_enabled", "AOF 是否开启"),
        ("aof_current_size", "当前 AOF 文件大小"),
        ("aof_base_size", "上次重写后的 AOF 大小"),
        ("aof_pending_rewrite", "是否有正在等待的重写"),
        ("aof_rewrite_in_progress", "AOF 重写是否正在进行"),
        ("aof_last_rewrite_time_sec", "上次重写耗时(秒)"),
        ("aof_last_bgrewrite_status", "上次重写状态"),
        ("aof_delayed_fsync", "延迟 fsync 的次数"),
    ]

    for key, desc in aof_fields:
        if key in info:
            val = info[key]
            color = Color.SUCCESS
            if key == "aof_last_bgrewrite_status" and val != "ok":
                color = Color.ERROR
            elif key == "aof_delayed_fsync" and isinstance(val, (int, float)) and val > 0:
                color = Color.WARNING

            # 格式化大小
            if key in ("aof_current_size", "aof_base_size") and isinstance(val, (int, float)) and val > 1024:
                val_display = f"{val:,} 字节"
                print(f"  {Color.DIM}{desc}:{Color.RESET} {color}{val_display}{Color.RESET}")
            else:
                print(f"  {Color.DIM}{desc}:{Color.RESET} {color}{val}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 9 步：展示 RDB vs AOF 对比总结
    # ═══════════════════════════════════════════════════════════
    print_step(9, "RDB vs AOF 对比 — 什么时候用哪个？")

    print(f"""
  ┌──────────────────┬─────────────────────────┬──────────────────────────┐
  │ 特性              │ RDB                     │ AOF                      │
  ├──────────────────┼─────────────────────────┼──────────────────────────┤
  │ 记录方式          │ 定时全量快照（拍照）      │ 逐条记录写操作（日志）    │
  │ 数据安全          │ 可能丢两次快照间的数据    │ everysec 最多丢 1 秒     │
  │ 恢复速度          │ ⭐⭐⭐ 极快               │ ⭐ 慢（需逐条重放）       │
  │ 文件体积          │ 小（压缩二进制）          │ 大（文本，需重写）        │
  │ 可读性            │ 不可读                   │ 可读（RESP 协议文本）    │
  │ 写入性能          │ 不影响（fork 子进程）     │ always 策略磁盘 IO 较重   │
  │ 适用场景          │ 缓存、计数器、排行榜      │ 支付订单、消息队列        │
  └──────────────────┴─────────────────────────┴──────────────────────────┘

  {Color.HIGHLIGHT}推荐组合（大多数场景）：{Color.RESET}
    RDB + AOF everysec + 混合持久化（aof-use-rdb-preamble yes）

  {Color.DIM}RDB 做快速恢复和定时备份，AOF 做细粒度保护。{Color.RESET}
  {Color.DIM}混合持久化让 AOF 恢复速度接近 RDB。{Color.RESET}
  """)

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
  {Color.SUCCESS}🎉 恭喜！你理解了 AOF 持久化的核心概念:{Color.RESET}

    {Color.HIGHLIGHT}AOF{Color.RESET}           = 把每次写操作记在本子上，断电后按本子重做
    {Color.HIGHLIGHT}appendfsync always{Color.RESET} = 次次刷盘——最安全，最慢
    {Color.HIGHLIGHT}appendfsync everysec{Color.RESET} = 每秒刷盘——推荐，最多丢 1 秒
    {Color.HIGHLIGHT}appendfsync no{Color.RESET} = 不刷盘——最快，最不安全
    {Color.HIGHLIGHT}Rewrite{Color.RESET}       = 读取当前状态生成精简 AOF，压缩日志
    {Color.HIGHLIGHT}混合持久化{Color.RESET}    = RDB 头 + AOF 尾，兼得速度与安全

  {Color.DIM}持久化（s11 + s12）是 Redis 可靠性的基础。{Color.RESET}
  {Color.DIM}下一章（s13）开始讲高可用——从一块黑板到多块黑板。{Color.RESET}
  """)

    # 清理演示数据
    client.delete(*client.keys("demo:aof:*"))
    print(f"  {Color.DIM}演示数据（demo:aof:*）已清理{Color.RESET}")
    print()

    # 询问是否清空整个数据库
    flush_db(client)


if __name__ == "__main__":
    main()
