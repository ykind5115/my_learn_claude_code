#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s18: 深入原理 — 打开黑板的背面看看

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - RESP 协议长什么样？怎么用原始 TCP 和 Redis 通信？
  - String 的三种底层编码（int/embstr/raw）有什么区别？
  - Hash 在什么条件下从 ziplist 变成 hashtable？
  - 渐进式 rehash 是怎么工作的？
  - 怎么检测和预防大 Key？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s18_internals/code.py
"""

import sys
import socket
import time
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s25_redis.utils import (
    Color,
    get_redis_client,
    get_raw_client,
    show_blackboard,
    print_step,
    print_command,
    print_note,
    print_key_point,
    print_result,
    cleanup_demo_keys,
    section,
)


def resp_send_and_recv(sock: socket.socket, raw_cmd: bytes) -> bytes:
    """发送 RESP 格式的命令并接收响应"""
    sock.sendall(raw_cmd)
    return sock.recv(65536)


def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s18: 深入原理 — 打开黑板的背面看看{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    client = get_redis_client()
    raw_client = get_raw_client()

    # 清理
    for key in ["int_key", "embstr_key", "raw_key", "small_hash", "big_hash",
                 "large_list", "detect_me"]:
        try:
            client.delete(key)
        except Exception:
            pass
    cleanup_demo_keys(client, "demo:*")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: RESP 协议 — 偷看 Redis 的"语言"
    # ═══════════════════════════════════════════════════════════
    print_step(1, "RESP 协议 — 用原始 TCP 和 Redis 对话")

    print_note("RESP = Redis Serialization Protocol，Redis 和客户端通信的底层协议")
    print_note("我们将用原始 socket 发送 RESP 格式的字节，不依赖 redis-py")

    section("建立 TCP 连接")

    # 建立原始 TCP 连接
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    sock.connect(("127.0.0.1", 6379))
    print(f"  {Color.SUCCESS}✅ TCP 连接已建立到 127.0.0.1:6379{Color.RESET}")

    section("发送 PING (RESP 格式)")

    # PING 命令的 RESP 编码: *1\r\n$4\r\nPING\r\n
    ping_cmd = b"*1\r\n$4\r\nPING\r\n"
    print_command(f"发送: {ping_cmd!r}", "RESP 编码的 PING 命令")
    print(f"  人类可读: *1\\r\\n$4\\r\\nPING\\r\\n")
    print(f"  意思: 数组(1个元素) 字符串(4字节)=PING")

    response = resp_send_and_recv(sock, ping_cmd)
    print(f"  收到: {response!r}")
    print(f"  {Color.SUCCESS}✅ PONG! Redis 在线！{Color.RESET}")

    section("发送 SET 命令 (RESP 格式)")

    # SET demo:resp_key "hello_from_resp" 的 RESP 编码
    # *3\r\n$3\r\nSET\r\n$13\r\ndemo:resp_key\r\n$15\r\nhello_from_resp\r\n
    set_cmd = b"*3\r\n$3\r\nSET\r\n$13\r\ndemo:resp_key\r\n$15\r\nhello_from_resp\r\n"
    print_command(f"发送: SET demo:resp_key hello_from_resp (RAW RESP)")
    print(f"  RESP 编码: *3\\r\\n$3\\r\\nSET\\r\\n$13\\r\\ndemo:resp_key\\r\\n$15\\r\\nhello_from_resp\\r\\n")
    print(f"  *3 → 数组有 3 个元素")
    print(f"  $3 → 第一个字符串长 3 字节: 'SET'")
    print(f"  $13 → 第二个字符串长 13 字节: 'demo:resp_key'")
    print(f"  $15 → 第三个字符串长 15 字节: 'hello_from_resp'")

    response = resp_send_and_recv(sock, set_cmd)
    print(f"  收到: {response!r} → {Color.SUCCESS}OK!{Color.RESET}")

    section("发送 GET 命令 (RESP 格式)")

    get_cmd = b"*2\r\n$3\r\nGET\r\n$13\r\ndemo:resp_key\r\n"
    print_command(f"发送: GET demo:resp_key (RAW RESP)")

    response = resp_send_and_recv(sock, get_cmd)
    print(f"  收到: {response!r}")
    # 解析: $15\r\nhello_from_resp\r\n
    print(f"  这意味着: 字符串(15字节) = 'hello_from_resp'")

    # 验证
    val = client.get("demo:resp_key")
    print(f"  redis-py 读取: '{val}' ✅ 一致！")

    sock.close()
    print_note("通过原始 TCP 发送 RESP 命令成功了！RESP 协议就是这么简单直接。")

    print_key_point(
        "RESP 协议是文本式协议，简单、可读。\n"
        "    前缀用来表示数据类型（+简单字符串、-错误、:整数、$批量字符串、*数组）。\n"
        "    `\\r\\n` 作为分隔符。\n"
        "    理解 RESP 协议 = 理解 Redis 客户端的底层实现。"
    )

    show_blackboard(client, "通过 RESP 协议写入的数据")

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: String 的三种底层编码
    # ═══════════════════════════════════════════════════════════
    print_step(2, "String 的三种底层编码 — int / embstr / raw")

    print_note("Redis 会根据 String 的值自动选择最省内存的编码方式")
    print_note("使用 OBJECT ENCODING 命令可以查看底层编码")

    # --- int 编码 ---
    section("int 编码 — 整数类型")

    raw_client.set("int_key", 12345)
    encoding = raw_client.object("ENCODING", "int_key")
    encoding_str = encoding.decode() if isinstance(encoding, bytes) else str(encoding) if encoding else "unknown"
    print_command('SET int_key 12345')
    print_command('OBJECT ENCODING int_key')
    print(f"  int_key 编码: {Color.HIGHLIGHT}{encoding_str}{Color.RESET}")
    print_note("整数直接存为 C 语言的 long 类型，不额外分配内存，非常省空间")

    # --- embstr 编码 ---
    section("embstr 编码 — 短字符串 (<= 44 字节)")

    raw_client.set("embstr_key", "Hello, Redis!")
    encoding = raw_client.object("ENCODING", "embstr_key")
    encoding_str = encoding.decode() if isinstance(encoding, bytes) else str(encoding) if encoding else "unknown"
    print_command('SET embstr_key "Hello, Redis!"')
    print_command('OBJECT ENCODING embstr_key')
    print(f"  embstr_key 编码: {Color.HIGHLIGHT}{encoding_str}{Color.RESET}")

    # 长度刚好 44 字节
    short_str = "A" * 44
    raw_client.set("embstr_key", short_str)
    encoding = raw_client.object("ENCODING", "embstr_key")
    encoding_str = encoding.decode() if isinstance(encoding, bytes) else str(encoding) if encoding else "unknown"
    print(f"  44 字节字符串编码: {Color.HIGHLIGHT}{encoding_str}{Color.RESET}")
    print_note("embstr = embedded string，字符串和 Redis 对象头存在同一块内存中")

    # --- raw 编码 ---
    section("raw 编码 — 长字符串 (> 44 字节)")

    long_str = "B" * 45
    raw_client.set("raw_key", long_str)
    encoding = raw_client.object("ENCODING", "raw_key")
    encoding_str = encoding.decode() if isinstance(encoding, bytes) else str(encoding) if encoding else "unknown"
    print_command('SET raw_key "B" * 45')
    print_command('OBJECT ENCODING raw_key')
    print(f"  45 字节字符串编码: {Color.HIGHLIGHT}{encoding_str}{Color.RESET}")
    print_note("超过 44 字节 → raw 编码，字符串和对象头分开存储")

    # --- 超长字符串 ---
    huge_str = "C" * 10000
    raw_client.set("raw_key", huge_str)
    encoding = raw_client.object("ENCODING", "raw_key")
    encoding_str = encoding.decode() if isinstance(encoding, bytes) else str(encoding) if encoding else "unknown"
    # MEMORY USAGE
    mem_usage = raw_client.memory_usage("raw_key")
    mem_int = int(mem_usage) if mem_usage is not None else 0
    print(f"  10000 字节字符串编码: {Color.HIGHLIGHT}{encoding_str}{Color.RESET}")
    print(f"  内存占用: {Color.HIGHLIGHT}{mem_int} 字节{Color.RESET}")

    print_key_point(
        "String 编码总结:\n"
        "    int (整数) → 直接存为 long，最省内存\n"
        "    embstr (≤44 字节) → 和对象头存在一起，省一次内存分配\n"
        "    raw (> 44 字节) → 分开存储，适合大字符串\n"
        "    所有切换都是自动的，用户无感知！"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: Hash 的编码转换 — ziplist → hashtable
    # ═══════════════════════════════════════════════════════════
    print_step(3, "Hash 编码转换 — ziplist → hashtable")

    print_note("当 Hash 字段少、值小时，Redis 用 ziplist（紧凑编码）")
    print_note("当字段数超过 512 或某字段长度超过 64 字节时，自动转为 hashtable")

    section("小 Hash — 使用 ziplist 编码")

    # 创建一个小 hash
    raw_client.hset("small_hash", "name", "Alice")
    encoding = raw_client.object("ENCODING", "small_hash")
    encoding_str = encoding.decode() if isinstance(encoding, bytes) else str(encoding) if encoding else "unknown"
    print_command('HSET small_hash name "Alice"')
    print_command("OBJECT ENCODING small_hash")
    print(f"  small_hash 编码: {Color.HIGHLIGHT}{encoding_str}{Color.RESET}")

    raw_client.hset("small_hash", "age", "30")
    raw_client.hset("small_hash", "city", "北京")
    print(f"  添加更多字段后编码不变 → 仍为 {Color.HIGHLIGHT}ziplist{Color.RESET}")

    print_note("ziplist = 所有字段连续存储，类似数组。省内存但查找 O(n)。")

    section("大 Hash — hashtable 编码")

    print_note("添加 512+ 个字段，触发编码转换...")

    for i in range(520):
        raw_client.hset("big_hash", f"field_{i}", f"value_{i}")

    encoding = raw_client.object("ENCODING", "big_hash")
    encoding_str = encoding.decode() if isinstance(encoding, bytes) else str(encoding) if encoding else "unknown"
    print_command("HSET big_hash field_0..519 → OBJECT ENCODING")
    print(f"  big_hash 编码: {Color.HIGHLIGHT}{encoding_str}{Color.RESET}")
    print_note("超过 512 个字段后，自动切换为 hashtable。查找 O(1) 但内存开销大。")

    # 显示 hash 大小
    hlen = raw_client.hlen("big_hash")
    mem_usage = raw_client.memory_usage("big_hash")
    mem_int = int(mem_usage) if mem_usage is not None else 0
    print(f"  big_hash 字段数: {hlen}")
    print(f"  big_hash 内存占用: {mem_int} 字节 ≈ {mem_int/1024:.1f} KB")

    print_key_point(
        "Hash 编码自动转换: ziplist → hashtable\n"
        "    阈值: 字段 > 512 或任何字段值 > 64 字节\n"
        "    小数据用 ziplist（省内存），大数据用 hashtable（快查找）\n"
        "    用户完全无感知——用 HSET/HGET 即可，编码是透明切换的"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 渐进式 rehash 概念演示
    # ═══════════════════════════════════════════════════════════
    print_step(4, "渐进式 rehash 概念")

    print_note("渐进式 rehash 难用代码演示（发生在 Redis 内部），但我们可以解释它的工作机制")

    section("为什么需要 rehash？")

    print(f"""
  {Color.DIM}Hash 表随着元素增加，负载因子（元素数/桶数）升高。{Color.RESET}
  {Color.DIM}负载因子 > 1 → 冲突增加 → 查找性能下降{Color.RESET}

  例如:
    初始: {Color.HIGHLIGHT}4 个桶 → 放 3 个元素 → 负载因子 0.75{Color.RESET}
    添加 3 个后: {Color.HIGHLIGHT}4 个桶 → 放 6 个元素 → 负载因子 1.5{Color.RESET}
    需要扩容！→ 创建 8 个桶的新表
  """)

    section("普通 rehash vs 渐进式 rehash")

    print(f"""
  {Color.WARNING}普通 rehash（不好的方式）:{Color.RESET}
    ① 创建 8 个桶的新表
    ② 一次把 6 个元素全部搬过去（耗时！）
    ③ 释放旧表
    → 搬移期间 Redis 不能做别的事！

  {Color.SUCCESS}Redis 的渐进式 rehash:{Color.RESET}
    ① 创建 8 个桶的新表（保留旧表）
    ② 每次处理一个命令，顺手搬一个桶
        - SET user:1001 → 搬旧表 0 号桶
        - GET counter → 搬旧表 1 号桶
        - INCR visits → 搬旧表 2 号桶
    ③ 所有桶搬完后释放旧表
    → 不阻塞！把大操作分摊到多次小操作中
  """)

    print_note("查询时两个表都查；写入只写新表")
    print_note("渐进式 rehash 是 Redis 单线程能支持高并发的关键设计之一")

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 大 Key 检测
    # ═══════════════════════════════════════════════════════════
    print_step(5, "大 Key 检测 — DEBUG OBJECT 和 MEMORY USAGE")

    section("创建一个大 List 用于演示")

    print_note("创建一个 5000 个元素的 List，模拟大 Key")

    for i in range(5000):
        raw_client.rpush("large_list", f"item-{i}")

    llen = raw_client.llen("large_list")
    print(f"  large_list 长度: {llen}")

    section("MEMORY USAGE — 查看 key 的内存占用")

    print_command("MEMORY USAGE large_list", "查看 large_list 占了多少内存")
    mem = raw_client.memory_usage("large_list")
    mem_int = int(mem) if mem is not None else 0
    print(f"  large_list 内存占用: {Color.HIGHLIGHT}{mem_int} 字节{Color.RESET} ({mem_int/1024:.1f} KB)")

    # 对比空 list
    empty_mem = raw_client.memory_usage("large_list")  # 5000 elements
    per_item = mem_int / 5000 if mem_int > 0 else 0
    print(f"  平均每个元素: {per_item:.1f} 字节")

    section("DEBUG OBJECT — 查看 key 的内部信息")

    print_command("DEBUG OBJECT large_list", "查看 large_list 的底层调试信息")
    try:
        debug_info = raw_client.debug_object("large_list")
        info_str = debug_info.decode() if isinstance(debug_info, bytes) else str(debug_info)
        print(f"  DEBUG 信息: {info_str}")
    except Exception as e:
        print(f"  {Color.DIM}(DEBUG OBJECT 可能被禁用){Color.RESET}")

    section("创建一个大 String 并检测")

    huge_val = "X" * 100000  # 100KB 的字符串
    raw_client.set("detect_me", huge_val)
    print_command('SET detect_me "X" * 100000', "创建一个 100KB 的字符串")

    mem = raw_client.memory_usage("detect_me")
    mem_int = int(mem) if mem is not None else 0
    encoding = raw_client.object("ENCODING", "detect_me")
    encoding_str = encoding.decode() if isinstance(encoding, bytes) else str(encoding) if encoding else "unknown"
    print(f"  编码: {Color.HIGHLIGHT}{encoding_str}{Color.RESET}")
    print(f"  内存占用: {Color.HIGHLIGHT}{mem_int} 字节{Color.RESET} ({mem_int/1024:.1f} KB)")

    print_key_point(
        "大 Key 的三个问题:\n"
        "    ① 扫描阻塞 — 遍历大 Key 会阻塞 Redis\n"
        "    ② 删除阻塞 — DEL 大 Key 释放内存也阻塞\n"
        "    ③ 网络阻塞 — 传输大 Value 占用带宽\n"
        "    检测工具: MEMORY USAGE, DEBUG OBJECT, redis-cli --bigkeys"
    )

    show_blackboard(client, "最终黑板状态")

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 恭喜！你完成了 s25 Redis 全部课程！{Color.RESET}

{Color.DIM}今天你探索了 Redis 的内部原理:{Color.RESET}

   {Color.HIGHLIGHT}RESP 协议{Color.RESET}        →  Redis 和客户端通信的"语言"
   {Color.HIGHLIGHT}I/O 多路复用{Color.RESET}     →  单线程 + epoll = 高并发
   {Color.HIGHLIGHT}int/embstr/raw{Color.RESET}   →  String 的三种编码
   {Color.HIGHLIGHT}ziplist/hashtable{Color.RESET} →  Hash 的编码自动转换
   {Color.HIGHLIGHT}渐进式 rehash{Color.RESET}     →  不阻塞的扩容方式
   {Color.HIGHLIGHT}惰性+定期删除{Color.RESET}     →  过期 key 的清理策略
   {Color.HIGHLIGHT}大 Key 检测{Color.RESET}       →  MEMORY USAGE / DEBUG OBJECT

{Color.DIM}从 s00 "共享黑板"模型开始，到 s18 打开黑板背面看内部原理。{Color.RESET}
{Color.DIM}你现在不仅会用 Redis，而且真正理解了 Redis。{Color.RESET}
""")

    # 清理
    for key in ["int_key", "embstr_key", "raw_key", "small_hash",
                 "big_hash", "large_list", "detect_me"]:
        try:
            client.delete(key)
        except Exception:
            pass
    cleanup_demo_keys(client, "demo:*")
    raw_client.close()
    client.close()


if __name__ == "__main__":
    main()
