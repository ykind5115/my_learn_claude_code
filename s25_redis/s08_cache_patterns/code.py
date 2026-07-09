#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s08: 缓存模式实战 — Cache-Aside、穿透、击穿、雪崩

═══════════════════════════════════════════════════════════════
学完本章你应该能回答：
  - Cache-Aside 模式的 4 步流程是什么？
  - 缓存穿透、击穿、雪崩分别是什么？有什么区别？
  - 布隆过滤器解决了什么问题？
  - 为什么更新时"删除缓存"比"更新缓存"安全？
═══════════════════════════════════════════════════════════════

启动方式:
    python s25_redis/s08_cache_patterns/code.py
"""

import sys
import json
import time
import random
import threading
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from s25_redis.utils import (
    Color, get_redis_client,
    show_blackboard, print_step, print_command,
    print_note, print_key_point, print_result,
    section, cleanup_demo_keys,
)


# ═══════════════════════════════════════════════════════════════
# 辅助函数：模拟数据库
# ═══════════════════════════════════════════════════════════════

class FakeDB:
    """模拟关系型数据库（字典）"""
    def __init__(self):
        self._data = {}

    def seed(self, key: str, value: dict):
        self._data[key] = value

    def get(self, key: str):
        print(f"  {Color.BG_YELLOW}[DB]  查询数据库: {key}{Color.RESET}")
        time.sleep(0.2)  # 模拟数据库查询延迟
        return self._data.get(key)

    def update(self, key: str, value: dict):
        print(f"  {Color.BG_YELLOW}[DB]  更新数据库: {key} = {value}{Color.RESET}")
        self._data[key] = value
        time.sleep(0.05)


# ═══════════════════════════════════════════════════════════════
# 辅助函数：模拟高并发
# ═══════════════════════════════════════════════════════════════

class AtomicCounter:
    """线程安全的计数器"""
    def __init__(self):
        self._lock = threading.Lock()
        self._value = 0

    def inc(self):
        with self._lock:
            self._value += 1
            return self._value

    @property
    def value(self):
        with self._lock:
            return self._value


# ═══════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  s08: 缓存模式实战 — 黑板是草稿纸，数据库是档案室{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    client = get_redis_client()
    client.flushdb()

    db = FakeDB()

    # 预先往"数据库"里写入一些数据
    db.seed("user:1001", {"name": "张三", "age": 28, "city": "北京"})
    db.seed("user:1002", {"name": "李四", "age": 35, "city": "上海"})

    print_note("数据库初始数据已就绪")
    print_note("黑板（Redis）是空的 — 还没任何缓存")

    show_blackboard(client, "初始状态 — 黑板上什么都没有", "demo:*")

    # ═══════════════════════════════════════════════════════════
    # 第 1 步: Cache-Aside 模式 — 查缓存 → miss → 查 DB → 写缓存
    # ═══════════════════════════════════════════════════════════
    print_step(1, "Cache-Aside 模式 — 第一次读取（cache miss）")

    user_id = "user:1001"
    cache_key = f"demo:cache:{user_id}"

    print_command(f"GET {cache_key}", "第一步：查缓存")
    cached = client.get(cache_key)
    print_result(cached, "缓存结果")

    if cached is None:
        print_note("缓存未命中 (cache miss) — 去数据库查")

        print_command(f"DB: SELECT * FROM users WHERE id = 1001", "第二步：查数据库")
        user_data = db.get(user_id)
        print_result(user_data, "数据库结果")

        print_command(f"SET {cache_key} <json> EX 300", "第三步：写入缓存（过期时间 300 秒）")
        client.setex(cache_key, 300, json.dumps(user_data, ensure_ascii=False))
        print_result("OK", "缓存写入")

    show_blackboard(client, "第一次读取后 — 缓存已建立", f"{cache_key}*")

    # 第二次读取 — 缓存命中
    print_command(f"GET {cache_key}", "第二次读取 — 查缓存")
    cached = client.get(cache_key)
    if cached is not None:
        print(f"  {Color.SUCCESS}→ 缓存命中 (cache hit)! 直接从黑板返回数据{Color.RESET}")
        data = json.loads(cached)
        print(f"  {Color.SUCCESS}  数据: {data}{Color.RESET}")
        print_note("不再查询数据库 — 这就是缓存的加速效果")

    print_key_point(
        "Cache-Aside 的四步流程:\n"
        "    ① 查缓存 (GET)\n"
        "    ② Miss → 查数据库 (SELECT)\n"
        "    ③ 写入缓存 (SETEX)\n"
        "    ④ 返回数据\n"
        "    \n"
        "    下次同样的请求，缓存命中 → 跳过 ②③ 两步，直接返回！"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 2 步: 更新数据 — 先更新 DB，再删除缓存
    # ═══════════════════════════════════════════════════════════
    print_step(2, "更新数据 — 先更新数据库，再删除缓存")

    print_note("用户 1001 改了名字：张三 → 张四")

    print_command("DB: UPDATE users SET name='张四' WHERE id=1001", "第一步：更新数据库")
    db.update("user:1001", {"name": "张四", "age": 28, "city": "北京"})

    print_command(f"DEL {cache_key}", "第二步：删除缓存（不是更新缓存！）")
    client.delete(cache_key)
    print_result("OK", "缓存已删除")

    show_blackboard(client, "更新后 — 缓存已被删除", f"{cache_key}*")
    print_note("下次读取时 → 缓存 miss → 从 DB 读最新数据 → 重建缓存")

    # 再次读取验证
    print_command(f"GET {cache_key}", "验证：再次读取")
    cached = client.get(cache_key)
    if cached is None:
        print_note("缓存不存在 → 从数据库读取最新数据")
        user_data = db.get(user_id)
        client.setex(cache_key, 300, json.dumps(user_data, ensure_ascii=False))
        cached = client.get(cache_key)
        data = json.loads(cached)
        print(f"  {Color.SUCCESS}→ 读到最新数据: {data}{Color.RESET}")

    print_key_point(
        "为什么是删除缓存，而不是更新缓存？\n"
        "    并发场景下，两个请求同时更新同一个数据：\n"
        "    请求 A 更新 DB → 请求 B 更新 DB → 请求 B 更新缓存 → 请求 A 更新缓存\n"
        "    最终缓存放了 A 的数据（不是最新的）!\n"
        "    \n"
        "    如果删除缓存：\n"
        "    请求 A 更新 DB → 请求 B 更新 DB → 请求 A 删缓存 → 请求 B 删缓存\n"
        "    下一次读 → miss → 从 DB 重建缓存 → 一定是最新的 ✅"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 3 步: 缓存穿透 — 查不存在的 key
    # ═══════════════════════════════════════════════════════════
    print_step(3, "缓存穿透 — 查一个不存在的 key")

    print_note("攻击者不断请求不存在的用户 user:99999")
    print_note("每次请求都穿过缓存，直接打到数据库")

    non_exist_key = "demo:cache:user:99999"
    miss_count = AtomicCounter()

    def request_non_exist():
        """模拟一个请求不存在的用户"""
        cached = client.get(non_exist_key)
        if cached is None:
            miss_count.inc()
            # 缓存 miss → 查数据库（也查不到）
            data = db.get("user:99999")
            if data is None:
                print(f"  {Color.WARNING}[穿透] 缓存 miss → DB 也查不到 → 直接穿透！{Color.RESET}")

    # 模拟 5 次穿透请求
    print_command(f"GET {non_exist_key}  × 5", "5 次请求不存在的用户")
    for i in range(5):
        request_non_exist()
    print(f"\n  {Color.ERROR}穿透次数: {miss_count.value} / 5{Color.RESET}")

    print_note("5 次请求全部穿透到数据库 — 如果并发 10000 次，DB 扛不住")

    # 解决方案：空值缓存
    print_step(3.1, "解决方案：空值缓存")

    print_note("即使数据库没有数据，也把「空」缓存起来，但过期时间很短")

    print_command(f"SET {non_exist_key} NULL EX 30", "空值缓存 — 30 秒过期")
    client.setex(non_exist_key, 30, "NULL")
    show_blackboard(client, "空值缓存已建立", f"{non_exist_key}*")

    # 再次请求 — 被空值缓存拦截
    miss_count2 = AtomicCounter()

    def request_with_null_cache():
        cached = client.get(non_exist_key)
        if cached is None:
            miss_count2.inc()
        elif cached == "NULL":
            print(f"  {Color.SUCCESS}[拦截] 空值缓存命中 → 不查 DB，直接返回{Color.RESET}")

    print_command(f"GET {non_exist_key}  × 5 (有空值缓存)", "5 次请求，观察是否穿透")
    for i in range(5):
        request_with_null_cache()
    print(f"\n  {Color.SUCCESS}穿透次数: {miss_count2.value} / 5 (所有请求都被空值缓存拦截){Color.RESET}")

    print_key_point(
        "缓存穿透的两种解决方案：\n"
        "    ① 空值缓存 — 即使 DB 没有，也在缓存中存一个「NULL」标记\n"
        "       优点：实现简单\n"
        "       缺点：需要设短 TTL，会存大量空 key\n"
        "    ② 布隆过滤器 — 在缓存前加一层过滤器\n"
        "       优点：空间效率极高\n"
        "       缺点：有误判率，需要额外维护"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 4 步: 缓存击穿 — 热点 key 过期
    # ═══════════════════════════════════════════════════════════
    print_step(4, "缓存击穿 — 热点 key 过期")

    hot_key = "demo:hot:data"
    # 先写入热点数据（短 TTL）
    client.setex(hot_key, 2, json.dumps({"hot": "data", "value": "热门内容"}))

    print_command(f"SET {hot_key} <data> EX 2", "设置热点数据，2 秒后过期")
    show_blackboard(client, "热点数据已缓存", f"{hot_key}*")

    print_note("等待 3 秒，热点 key 过期...")
    time.sleep(3)

    show_blackboard(client, "热点 key 已过期，黑板上没有了", f"{hot_key}*")

    print_note("现在模拟 10 个并发请求同时访问这个热点 key")
    print_note("如果没有互斥锁 → 10 个请求全部打到数据库！")

    db_hit_count = AtomicCounter()

    def request_hot_key(use_mutex: bool, thread_id: int):
        """模拟请求热点 key"""
        data = client.get(hot_key)
        if data is not None:
            print(f"  [线程 {thread_id}] 缓存命中 ✅")
            return

        if use_mutex:
            # 互斥锁方案
            lock_key = "demo:lock:hot:data"
            locked = client.set(lock_key, f"thread_{thread_id}", nx=True, ex=5)
            if locked:
                db_hit_count.inc()
                print(f"  {Color.BG_YELLOW}[线程 {thread_id}] 拿到锁 → 查 DB...{Color.RESET}")
                time.sleep(0.1)
                # 查 DB + 写缓存
                result = {"hot": "data", "from": "db", "time": time.time()}
                client.setex(hot_key, 10, json.dumps(result))
                client.delete(lock_key)
                print(f"  {Color.SUCCESS}[线程 {thread_id}] 缓存已重建{Color.RESET}")
            else:
                print(f"  [线程 {thread_id}] 没拿到锁 → 等待重试")
                time.sleep(0.2)
                # 重试（简化版）
                data = client.get(hot_key)
                if data:
                    print(f"  {Color.SUCCESS}[线程 {thread_id}] 重试成功，缓存已命中{Color.RESET}")
        else:
            # 无互斥锁 — 全部打 DB
            db_hit_count.inc()
            print(f"  {Color.ERROR}[线程 {thread_id}] [击穿] 直接查 DB!{Color.RESET}")
            time.sleep(0.1)
            result = {"hot": "data", "from": "db", "time": time.time()}
            client.setex(hot_key, 10, json.dumps(result))

    print_command("10 个并发请求（无锁）", "模拟缓存击穿")
    threads = []
    for i in range(10):
        t = threading.Thread(target=request_hot_key, args=(False, i))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    print(f"\n  {Color.WARNING}无锁情况下，数据库被请求了 {db_hit_count.value} 次{Color.RESET}")
    print_note("如果并发 10000 → DB 被打挂")

    # 演示互斥锁方案
    print_step(4.1, "解决方案：互斥锁")

    # 让 key 再次过期
    client.delete(hot_key)
    print_command(f"DEL {hot_key}", "清除缓存，模拟再次过期")
    time.sleep(0.5)

    db_hit_count2 = AtomicCounter()

    print_command("10 个并发请求（有互斥锁）", "模拟缓存击穿 + 互斥锁保护")
    threads = []
    for i in range(10):
        t = threading.Thread(target=request_hot_key, args=(True, i))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    print(f"\n  {Color.SUCCESS}有互斥锁情况下，数据库只被请求了 {db_hit_count2.value} 次{Color.RESET}")
    print_note("只有拿到锁的那个线程查了 DB，其他线程等待重试 → 保护了数据库")

    print_key_point(
        "缓存击穿 vs 缓存穿透：\n"
        "    缓存穿透：查的数据在 DB 和缓存中都不存在\n"
        "    缓存击穿：数据在 DB 中存在，但缓存中刚好过期了\n"
        "    \n"
        "    击穿是「热点 key 过期」的问题\n"
        "    穿透是「不存在的数据」的问题\n"
        "    两者是完全不同的场景，解法也不同！"
    )

    # ═══════════════════════════════════════════════════════════
    # 第 5 步: 缓存雪崩 — 大量 key 同时过期
    # ═══════════════════════════════════════════════════════════
    print_step(5, "缓存雪崩 — 大量 key 同时过期")

    print_note("假设有 10 个商品，全部设置了相同的过期时间 5 秒")
    print_note("5 秒后它们全部同时过期 → 所有请求同时打到数据库")

    # 设置 10 个相同的 TTL
    print_command("SET product:1...10 EX 5", "全部设相同过期时间")
    for i in range(1, 11):
        client.setex(f"demo:product:{i}", 5, json.dumps({"id": i, "name": f"商品 {i}"}))

    show_blackboard(client, "10 个商品全部缓存，TTL 都是 5 秒", "demo:product:*")

    print_note("等待 6 秒... 所有 key 同时过期")
    time.sleep(6)

    show_blackboard(client, "雪崩 — 所有 key 同时消失", "demo:product:*")
    print(f"  {Color.ERROR}所有商品 key 同时过期 → 10 个请求全部打向数据库！{Color.RESET}")

    # 演示随机 TTL
    print_step(5.1, "解决方案：随机 TTL")

    print_note("给每个 key 加上随机偏移量，让过期时间分散")
    print_command("SET product:1...10 EX (3600 + random 0~600)", "加随机偏移量")

    for i in range(1, 11):
        ttl = 10 + random.randint(0, 20)  # 10~30 秒
        client.setex(f"demo:product:{i}", ttl, json.dumps({"id": i, "name": f"商品 {i}"}))

    show_blackboard(client, "随机 TTL — 过期时间分散了", "demo:product:*")
    print_note("这些 key 不会同时过期 — 数据库压力被分散了")

    print_key_point(
        "缓存三种问题的区分：\n"
        "    穿透 (Penetration)  → 查不存在的数据         → 空值缓存 / 布隆过滤器\n"
        "    击穿 (Breakdown)    → 单个热点 key 过期      → 互斥锁 / 永不过期\n"
        "    雪崩 (Avalanche)    → 大量 key 同时过期      → 随机 TTL / 多级缓存\n"
        "    \n"
        "    中文名称很形象：\n"
        "      - 穿透：像子弹穿过了缓存层\n"
        "      - 击穿：缓存层被砸了一个洞\n"
        "      - 雪崩：缓存层大面积崩塌"
    )

    # ═══════════════════════════════════════════════════════════
    # 演示结束
    # ═══════════════════════════════════════════════════════════
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"{Color.HEADER}  演示结束！{Color.RESET}")
    print(f"{Color.HEADER}{'═' * 65}{Color.RESET}")

    print(f"""
{Color.SUCCESS}🎉 你掌握了四种缓存实用模式！{Color.RESET}

   {Color.HIGHLIGHT}Cache-Aside{Color.RESET}    →  查缓存 → miss → 查 DB → 写缓存 → 返回
   {Color.HIGHLIGHT}空值缓存{Color.RESET}      →  解决缓存穿透（不存在的数据也缓存）
   {Color.HIGHLIGHT}互斥锁{Color.RESET}        →  解决缓存击穿（热点 key 过期）
   {Color.HIGHLIGHT}随机 TTL{Color.RESET}      →  解决缓存雪崩（大量 key 同时过期）

{Color.DIM}核心原则：先更新 DB，再删除缓存 — 绝不更新缓存！{Color.RESET}
""")

    cleanup_demo_keys(client, "demo:*")
    client.flushdb()


if __name__ == "__main__":
    main()
