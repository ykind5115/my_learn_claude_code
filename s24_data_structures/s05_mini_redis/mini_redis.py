#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini Redis — 基于哈希表的键值存储

Redis 的核心就是一个「增强版哈希表」:
  - O(1) 的 SET/GET/DELETE
  - 支持 TTL (过期时间)
  - 支持多种数据类型

═══════════════════════════════════════════════════════════════
你的任务: 实现 MiniRedis 类中标记为 TODO 的方法。
底层 HashTable 已经实现好了。
"""

import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from s05_mini_redis.hash_table import HashTable
import time


class MiniRedis:
    """迷你 Redis — 基于哈希表"""

    def __init__(self):
        self.store = HashTable()  # 主存储
        self.expiry = {}          # key → 过期时间戳

    def set(self, key, value, ttl=None):
        """
        设置键值对。

        参数:
          key: 键
          value: 值
          ttl: 过期时间(秒), None 表示永不过期

        提示:
          1. self.store.put(key, value)
          2. 如果 ttl 不为 None: self.expiry[key] = time.time() + ttl
        """
        # TODO: 实现 set
        raise NotImplementedError("TODO: 实现 set")

    def get(self, key, default=None):
        """
        获取键的值。如果 key 已过期，返回 default 并删除 key。

        提示:
          1. 检查 key 是否在 expiry 中且已过期
          2. 如果过期: 删除 key，返回 default
          3. 否则: 返回 self.store.get(key, default)
        """
        # TODO: 实现 get
        raise NotImplementedError("TODO: 实现 get")

    def delete(self, key):
        """
        删除键值对。
        返回: True (已删除) 或 False (key 不存在)
        """
        # TODO: 实现 delete
        raise NotImplementedError("TODO: 实现 delete")

    def exists(self, key):
        """检查 key 是否存在且未过期"""
        return self.get(key, _SENTINEL) is not _SENTINEL

    def keys(self):
        """返回所有有效的 key (排除已过期的)"""
        now = time.time()
        result = []
        for key in self.store.keys():
            if key in self.expiry and self.expiry[key] <= now:
                continue
            result.append(key)
        return result

    def ttl(self, key):
        """返回 key 的剩余过期时间 (秒)，-1 表示永不过期，-2 表示 key 不存在"""
        val = self.store.get(key, _SENTINEL)
        if val is _SENTINEL:
            return -2
        if key not in self.expiry:
            return -1
        remaining = self.expiry[key] - time.time()
        return max(0, remaining)


_SENTINEL = object()  # 用于区分 "None 值" 和 "key 不存在"


class DemoMiniRedis(MiniRedis):
    """演示用完整实现"""

    def set(self, key, value, ttl=None):
        self.store.put(key, value)
        if ttl is not None:
            self.expiry[key] = time.time() + ttl
        elif key in self.expiry:
            del self.expiry[key]

    def get(self, key, default=None):
        if key in self.expiry and self.expiry[key] <= time.time():
            self.delete(key)
            return default
        return self.store.get(key, default)

    def delete(self, key):
        self.expiry.pop(key, None)
        return self.store.delete(key)
