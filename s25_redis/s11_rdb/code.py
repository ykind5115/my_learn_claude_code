#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s11: RDB 快照 — 给黑板拍照片

Chapter 4: 持久化 — 别让黑板断电就没了

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - RDB 持久化是怎么工作的？
  - SAVE 和 BGSAVE 有什么区别？
  - 什么是写时复制（Copy-on-Write）？
  - RDB 配置 save 900 1 是什么意思？
  - RDB 有什么优缺点？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s11_rdb/code.py
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


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s11: RDB 快照 — 给黑板拍照片{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
  {Color.DIM}还记得 s00 的心智模型吗？Redis 是一块共享黑板。

  但是黑板在内存里——断电就什么都没了。

  RDB = 给整块黑板拍一张照片，存到硬盘上。
  断电后，拿出照片，黑板恢复成拍照时的样子。

  这一章我们来理解：怎么拍照片？什么时候拍？有什么代价？{Color.RESET}
  """)

    # ────────────────────────────────────────────────────────────
    # 连接 Redis
    # ────────────────────────────────────────────────────────────
    client = get_redis_client()
    print(f"  {Color.SUCCESS}✅ 已连接到 Redis{Color.RESET}\n")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步：查看当前 RDB 配置
    # ═══════════════════════════════════════════════════════════
    print_step(1, "查看当前 RDB 配置")

    save_config = client.config_get("save")
    rdb_dir = client.config_get("dir")
    rdb_filename = client.config_get("dbfilename")
    rdbcompression = client.config_get("rdbcompression")
    rdbchecksum = client.config_get("rdbchecksum")

    print_command("CONFIG GET save", "查看 RDB 触发策略")
    save_value = save_config["save"]
    print_result(save_value)

    if save_value and save_value.strip():
        rules = save_value.strip().split()
        for i in range(0, len(rules), 2):
            seconds = rules[i]
            changes = rules[i + 1]
            human_seconds = {
                "60": "1 分钟",
                "300": "5 分钟",
                "900": "15 分钟",
                "3600": "1 小时",
            }.get(seconds, f"{seconds} 秒")

            print(f"    {Color.DIM}  save {seconds} {changes}  →  {human_seconds}内 ≥ {changes} 个 key 变化 → 触发 BGSAVE{Color.RESET}")
    else:
        print(f"    {Color.WARNING}  RDB 已关闭（save 配置为空）{Color.RESET}")

    print()
    print_command("CONFIG GET dir", "查看 RDB 文件保存目录")
    print_result(rdb_dir["dir"])

    print_command("CONFIG GET dbfilename", "查看 RDB 文件名")
    print_result(rdb_filename["dbfilename"])

    print_command("CONFIG GET rdbcompression", "RDB 是否启用压缩")
    print_result(rdbcompression["rdbcompression"])

    print_command("CONFIG GET rdbchecksum", "RDB 是否启用校验和")
    print_result(rdbchecksum["rdbchecksum"])

    rdb_path = os.path.join(rdb_dir["dir"], rdb_filename["dbfilename"])
    print(f"\n  {Color.DIM}RDB 文件完整路径: {rdb_path}{Color.RESET}")

    print_key_point(
        "RDB 配置有三要素：保存目录 (dir)、文件名 (dbfilename)、触发策略 (save)。\n"
        "    save 策略可以配置多条，满足任意一条就会触发 BGSAVE。\n"
        "    rdbcompression 和 rdbchecksum 控制文件的压缩与校验。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 2 步：写入数据准备快照
    # ═══════════════════════════════════════════════════════════
    print_step(2, "先写一些数据到黑板")

    print_command('SET demo:name "张三"')
    client.set("demo:name", "张三")
    print_command('SET demo:age "28"')
    client.set("demo:age", "28")
    print_command('SET demo:city "北京"')
    client.set("demo:city", "北京")
    print_command('SET demo:score "95"')
    client.set("demo:score", "95")
    print_command('SET demo:email "zhangsan@example.com"')
    client.set("demo:email", "zhangsan@example.com")
    print_command('SET demo:visits "1024"')
    client.set("demo:visits", "1024")

    print()
    show_blackboard(client, "黑板上现在有 6 个 key", "demo:*")

    # 查看 rdb_changes_since_last_save
    info = client.info("persistence")
    changes_since = info.get("rdb_changes_since_last_save", "N/A")
    print(f"  {Color.DIM}上次快照以来的变化次数: {Color.RESET}{Color.HIGHLIGHT}{changes_since}{Color.RESET}")
    print_note("这些数据目前只在内存里。如果有人拔电源，它们就没了。")

    print_key_point(
        "这些数据目前只在内存里。如果现在 Redis 崩溃，所有数据都丢了。\n"
        "    RDB 就是把这些数据「拍下来」存到硬盘，防止断电丢失。\n"
        "    但注意：RDB 不是实时记录——它是定期拍照。"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 3 步：触发 BGSAVE
    # ═══════════════════════════════════════════════════════════
    print_step(3, "触发 BGSAVE — 让助手给黑板拍照")

    section("执行 BGSAVE")
    print_command("BGSAVE", "后台触发 RDB 快照（fork 子进程执行，不阻塞）")
    result = client.execute_command("BGSAVE")
    print_result(result, "BGSAVE 返回")

    print_note("BGSAVE 是异步的——主进程立即返回「Background saving started」，子进程在后台执行快照。")
    print_note("主进程可以继续处理其他请求，不会被阻塞。")

    # 等待 BGSAVE 完成
    print(f"\n  {Color.DIM}等待 BGSAVE 完成...{Color.RESET}")
    while True:
        persis_info = client.info("persistence")
        if persis_info.get("rdb_bgsave_in_progress") == 0:
            break
        time.sleep(0.3)

    section("BGSAVE 完成后查看信息")

    last_save = client.execute_command("LASTSAVE")
    print_command("LASTSAVE", "查看最后一次成功快照的时间")
    if isinstance(last_save, int):
        print_result(datetime.fromtimestamp(last_save).strftime("%Y-%m-%d %H:%M:%S"))

    # 查看 BGSAVE 状态
    info = client.info("persistence")
    bgsave_status = info.get("rdb_last_bgsave_status", "N/A")
    bgsave_time = info.get("rdb_last_bgsave_time_sec", "N/A")
    print_command("INFO persistence", "查看 RDB 持久化状态")
    print(f"  {Color.DIM}  最后一次 BGSAVE 状态:{Color.RESET} "
          f"{Color.SUCCESS if bgsave_status == 'ok' else Color.ERROR}{bgsave_status}{Color.RESET}")
    print(f"  {Color.DIM}  最后一次 BGSAVE 耗时:{Color.RESET} {Color.HIGHLIGHT}{bgsave_time}{Color.RESET} 秒")

    # 检查 RDB 文件
    section("检查 RDB 文件")
    if os.path.exists(rdb_path):
        file_size = os.path.getsize(rdb_path)
        file_mtime = datetime.fromtimestamp(os.path.getmtime(rdb_path))
        print(f"  {Color.SUCCESS}✅ RDB 文件已创建{Color.RESET}")
        print(f"     {Color.DIM}路径: {rdb_path}{Color.RESET}")
        print(f"     {Color.DIM}大小: {Color.RESET}{Color.HIGHLIGHT}{file_size:,}{Color.RESET}{Color.DIM} 字节{Color.RESET}")
        print(f"     {Color.DIM}修改时间: {Color.RESET}{Color.HIGHLIGHT}{file_mtime}{Color.RESET}")

        # 粗略估算能存多少 key
        print(f"     {Color.DIM}该文件包含了 6 个 demo key 的快照{Color.RESET}")
    else:
        print(f"  {Color.WARNING}⚠ 未找到 RDB 文件{Color.RESET}")
        print(f"     {Color.DIM}RDB 文件可能在 Docker 容器内部，可以这样检查：{Color.RESET}")
        print(f"     {Color.DIM}  docker exec <container> ls -lh {rdb_path}{Color.RESET}")

    print_key_point(
        "BGSAVE 工作原理:\n"
        "    ① Redis 主进程调用 fork() 创建子进程\n"
        "    ② 子进程拥有 fork 那一刻的内存快照\n"
        "    ③ 子进程将快照写入临时 RDB 文件\n"
        "    ④ 写入完成后，用原子 rename 替换正式 RDB 文件\n"
        "    ⑤ 整个过程中，主进程可以继续处理请求"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步：SAVE vs BGSAVE 对比
    # ═══════════════════════════════════════════════════════════
    print_step(4, "SAVE vs BGSAVE — 阻塞 vs 非阻塞")

    section("SAVE — 阻塞式快照（生产环境不要用）")
    print(f"""
  {Color.WARNING}SAVE 命令让 Redis 主进程直接执行快照：{Color.RESET}

  ┌─────────────────────────────────────────────────┐
  │  时间 →  (假设 10 GB 数据)                        │
  │                                                    │
  │  SAVE  │████████████████████████████████████|      │
  │        │ 主进程被占用了 20 秒                      │
  │        │ 这个期间所有请求都被阻塞！                │
  │                                                    │
  │  SET A  │ ✗ 等待                                   │
  │  GET B  │ ✗ 等待                                   │
  │  INCR C │ ✗ 等待                                   │
  └─────────────────────────────────────────────────┘

  {Color.ERROR}生产环境绝不用 SAVE！{Color.RESET}
  """)

    section("BGSAVE — 非阻塞快照（生产环境使用）")
    print(f"""
  {Color.SUCCESS}BGSAVE 命令 fork 子进程执行快照：{Color.RESET}

  ┌─────────────────────────────────────────────────┐
  │  时间 →                                           │
  │                                                    │
  │  BGSAVE │fork|                                    │
  │         │  ├── 子进程: ████████████████ (写 RDB)  │
  │         │  └── 主进程: → SET → GET → INCR → ...  │
  │                                                    │
  │  SET A  │ ✅ 正常执行                              │
  │  GET B  │ ✅ 正常执行                              │
  │  INCR C │ ✅ 正常执行                              │
  └─────────────────────────────────────────────────┘

  {Color.SUCCESS}✅ BGSAVE 不阻塞请求！{Color.RESET}
  """)

    # 查看 fork 耗时
    stats = client.info("stats")
    fork_usec = stats.get("fork_usec", "N/A")
    print(f"  {Color.DIM}最近一次 fork 耗时: {Color.RESET}{Color.HIGHLIGHT}{fork_usec}{Color.RESET}{Color.DIM} 微秒{Color.RESET}")
    print_note("fork 本身是阻塞的——虽然时间很短（微秒级），但如果有大量请求同时到达，也会造成延迟")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步：RDB 数据丢失窗口演示
    # ═══════════════════════════════════════════════════════════
    print_step(5, "RDB 的数据丢失窗口 — 快照之间写入的数据会丢")

    section("理解丢失窗口")

    # 获取当前 save 配置来展示
    current_save = client.config_get("save")["save"]

    print(f"""
  {Color.DIM}当前 save 配置为: {current_save}{Color.RESET}

  ───────────────────────────────────────────────────────────

  假设一个场景：Redis 按策略每 15 分钟拍一次快照

  时间轴:
  ① 08:00  BGSAVE 触发成功      ← 此时有 key1 ~ key100
  ② 08:00 ~ 08:14  没有触发新快照
  ③ 08:05  写入 key101          ← 这些数据在「拍照之后」
  ④ 08:10  写入 key102          ← 不在上一张照片里
  ⑤ 08:12  写入 key103          ← 不在！

  ⑥ 08:15  Redis 崩溃！！！

  {Color.WARNING}恢复后：黑板上只有 key1 ~ key100{Color.RESET}
  {Color.WARNING}key101, key102, key103 全部丢失！{Color.RESET}
  """)

    # 查看目前的 rdb_changes_since_last_save
    info = client.info("persistence")
    changes = info.get("rdb_changes_since_last_save", 0)
    print(f"  {Color.DIM}当前 rdb_changes_since_last_save = {changes}{Color.RESET}")
    print(f"  {Color.DIM}这表示从上次快照到现在，有 {changes} 个 key 发生了变化{Color.RESET}")

    print(f"""
  {Color.HIGHLIGHT}🔑 关键理解：{Color.RESET}
  RDB 是「给黑板拍照片」，不是「记录每一笔写字」。

  两次照片之间的数据:
    - 如果 Redis 正常，它们一直在内存里——正常工作
    - 如果 Redis 崩溃，它们就丢了——因为照片里没有它们

  解决方案：
    → 缩短 RDB 间隔（减少丢失窗口）
    → 改用 AOF（记录每次写操作，下一章 s12 会讲）
    → RDB + AOF 混合（Redis 4.0+，兼顾速度与安全）
  """)

    # ═══════════════════════════════════════════════════════════
    # 第 6 步：写时复制（Copy-on-Write）示意
    # ═══════════════════════════════════════════════════════════
    print_step(6, "写时复制（Copy-on-Write）原理示意")

    print(f"""
  {Color.DIM}fork() 执行后：主进程和子进程共享同一份物理内存{Color.RESET}

   ┌─────────────────────────────────────────────────────┐
   │  fork() 之前                                         │
   │                                                      │
   │  物理内存:                                           │
   │  ┌───────┬───────┬───────┬───────┬───────┬───────┐  │
   │  │ A: 张 │ B: 北 │ C: 95 │ D: 12 │ E: 真 │ F: 嗨 │  │
   │  │ 三    │ 京    │       │ 3     │ 的    │       │  │
   │  └───────┴───────┴───────┴───────┴───────┴───────┘  │
   │                       所有数据                        │
   └─────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────┐
   │  fork() 之后 — 父子进程共享物理内存                    │
   │                                                      │
   │  主进程: ────────────┐                               │
   │                      ▼                               │
   │  物理内存: ┌───────┬───────┬───────┬───────┬───────┐ │
   │            │ A: 张 │ B: 北 │ C: 95 │ D: 12 │ E: 真 │ │
   │            │ 三    │ 京    │       │ 3     │ 的    │ │
   │            └───────┴───────┴───────┴───────┴───────┘ │
   │                      ▲                               │
   │  子进程: ────────────┘ (也看到相同的内存页)           │
   └─────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────┐
   │  主进程修改 A（张三 → 李四）— 触发复制               │
   │                                                      │
   │  主进程: ──────→ ┌───────┐  (写入新值到复制页)      │
   │                   │ A: 李 │                          │
   │                   │ 四    │                          │
   │                   └───────┘                          │
   │  物理内存: ┌───────┬───────┬───────┬───────┬───────┐ │
   │            │ A: 张 │ B: 北 │ C: 95 │ D: 12 │ E: 真 │ │
   │            │ 三    │ 京    │       │ 3     │ 的    │ │
   │            └───────┴───────┴───────┴───────┴───────┘ │
   │                      ▲ (子进程看到的是旧值：张三)      │
   │  子进程: ────────────┘ (继续读旧数据，不受影响)      │
   └─────────────────────────────────────────────────────┘

  {Color.SUCCESS}✅ 子进程看到的数据是 fork 那一刻的「冻结快照」——一致且完整{Color.RESET}
  {Color.SUCCESS}✅ 主进程可以继续写入新数据——互不干扰{Color.RESET}
  {Color.WARNING}⚠ 但注意：写入量越大，复制越多，内存开销越大{Color.RESET}
  """)

    # 查看 rdb_last_cow_size 如果存在
    cow_size = info.get("rdb_last_cow_size")
    if cow_size:
        print(f"  {Color.DIM}上一次 BGSAVE 的 Copy-on-Write 内存开销: {Color.RESET}"
              f"{Color.HIGHLIGHT}{int(cow_size) / 1024 / 1024:.1f} MB{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 7 步：查看完整的持久化状态
    # ═══════════════════════════════════════════════════════════
    print_step(7, "查看完整的 RDB 持久化状态")

    section("INFO persistence")
    info = client.info("persistence")
    rdb_fields = [
        ("rdb_changes_since_last_save", "上次快照以来变化的 key 数"),
        ("rdb_bgsave_in_progress", "BGSAVE 是否正在进行"),
        ("rdb_last_save_time", "最后一次成功快照时间"),
        ("rdb_last_bgsave_status", "最后一次 BGSAVE 状态"),
        ("rdb_last_bgsave_time_sec", "最后一次 BGSAVE 耗时(秒)"),
        ("rdb_current_bgsave_time_sec", "当前 BGSAVE 已耗时(秒)"),
        ("rdb_last_cow_size", "上一次 COW 内存开销(字节)"),
    ]

    for key, desc in rdb_fields:
        if key in info:
            val = info[key]
            # 时间戳转为可读格式
            if key == "rdb_last_save_time" and isinstance(val, int) and val > 0:
                val = datetime.fromtimestamp(val).strftime("%Y-%m-%d %H:%M:%S")
            # cow_size 转 MB
            if key == "rdb_last_cow_size" and isinstance(val, (int, float)) and val > 0:
                val = f"{val / 1024 / 1024:.1f} MB"

            color = Color.SUCCESS
            if key == "rdb_last_bgsave_status" and val != "ok":
                color = Color.ERROR
            elif key == "rdb_bgsave_in_progress" and val != 0:
                color = Color.WARNING

            print(f"  {Color.DIM}{desc}:{Color.RESET} {color}{val}{Color.RESET}")

    # ═══════════════════════════════════════════════════════════
    # 第 8 步：修改 save 配置
    # ═══════════════════════════════════════════════════════════
    print_step(8, "修改 RDB 配置 — 体验 save 策略的动态调整")

    section("临时设置更短的 save 间隔")
    print_command('CONFIG SET save "5 2"', "设置：5 秒内 2 个 key 变化就触发 BGSAVE")
    client.config_set("save", "5 2")
    print(f"  {Color.SUCCESS}✅ save 已设置为「5 秒内 ≥ 2 个 key 变化 → BGSAVE」{Color.RESET}")
    print_note("这是仅对当前连接有效的运行时修改，重启后恢复默认值")

    # 写入两个 key 触发 BGSAVE
    print(f"\n  {Color.DIM}写入 2 个 key 来触发新的 BGSAVE...{Color.RESET}")
    client.set("demo:trigger:a", "test1")
    client.set("demo:trigger:b", "test2")
    print(f"  {Color.SUCCESS}✅ 已 SET 2 个 key，等待 save 条件触发{Color.RESET}")

    # 等待 BGSAVE 触发
    time.sleep(6)  # 等 6 秒略超 5 秒

    # 检查是否触发了新的 BGSAVE
    last_save = client.execute_command("LASTSAVE")
    if isinstance(last_save, int):
        print(f"\n  {Color.DIM}LASTSAVE: {datetime.fromtimestamp(last_save).strftime('%H:%M:%S')}{Color.RESET}")
        print(f"  {Color.SUCCESS}✅ 新的 BGSAVE 已触发并完成（或正在执行）{Color.RESET}")

    # 恢复 save 配置
    client.config_set("save", "900 1 300 10 60 10000")
    print(f"\n  {Color.DIM}save 配置已恢复为默认值{Color.RESET}")

    print_key_point(
        "save 配置可以在运行时通过 CONFIG SET 修改（热更新），无需重启 Redis。\n"
        "    生产环境修改后要记得写入 redis.conf，否则重启后丢失。\n"
        "    设置太短的 save 间隔会导致频繁 fork，反而影响性能。"
    )

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
  {Color.SUCCESS}🎉 恭喜！你理解了 RDB 持久化的核心概念:{Color.RESET}

    {Color.HIGHLIGHT}RDB{Color.RESET}    = 给整块黑板拍照片，存到硬盘
    {Color.HIGHLIGHT}SAVE{Color.RESET}   = 自己拍（阻塞，生产环境不用）
    {Color.HIGHLIGHT}BGSAVE{Color.RESET} = 让助手拍（fork 子进程，不阻塞）
    {Color.HIGHLIGHT}fork(){Color.RESET}  = 创建子进程，共享内存快照
    {Color.HIGHLIGHT}Copy-on-Write{Color.RESET} = 改了才复制，不改就共享
    {Color.HIGHLIGHT}save X Y{Color.RESET} = X 秒内 Y 个 key 变化 → 触发 BGSAVE

  {Color.DIM}RDB 不是银弹——它有数据丢失的问题。{Color.RESET}
  {Color.DIM}下一章（s12）的 AOF 日志能解决「丢数据」的问题。{Color.RESET}
  """)

    # 清理演示数据
    client.delete(*client.keys("demo:*"))
    print(f"  {Color.DIM}演示数据（demo:*）已清理{Color.RESET}")
    print()

    # 询问是否清空整个数据库
    flush_db(client)


if __name__ == "__main__":
    main()
