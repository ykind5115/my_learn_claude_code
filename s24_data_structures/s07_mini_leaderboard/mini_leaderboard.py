#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini Leaderboard — 基于跳表的游戏排行榜

═══════════════════════════════════════════════════════════════
核心需求:
  1. 百万玩家，随时有人分数变化 → 插入/更新 O(log n)
  2. 随时查「某人的排名」→ rank O(log n)
  3. 随时查「Top 100」→ O(100)
  4. 范围查询「1000~2000 名」→ 支持

你的任务: 实现 Leaderboard 类中标记为 TODO 的方法。
底层 SkipList 已实现。
"""

import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from s07_mini_leaderboard.skip_list import SkipList


class Leaderboard:
    """游戏排行榜 — 基于跳表"""

    def __init__(self):
        self.scores = SkipList()  # score → player_name
        self.players = {}         # player_name → score (反向索引)

    def update_score(self, player, new_score):
        """
        更新玩家分数。

        如果玩家已存在: 删除旧分数，插入新分数。
        如果玩家不存在: 直接插入。

        提示:
          1. 检查 player 是否在 self.players 中
          2. 如果在: 用 self.scores.delete(旧分数) 删除
          3. self.scores.insert(new_score, player)
          4. 更新 self.players[player] = new_score
        """
        # TODO: 实现 update_score
        raise NotImplementedError("TODO: 实现 update_score")

    def get_rank(self, player):
        """
        获取玩家排名 (1-based, 1 = 最高分)。

        提示: self.scores.get_rank(score)
        """
        # TODO: 实现 get_rank
        raise NotImplementedError("TODO: 实现 get_rank")

    def get_top_n(self, n=10):
        """获取 Top N 玩家"""
        return self.scores.top_n(n)

    def get_score(self, player):
        """获取玩家分数"""
        return self.players.get(player, None)


class DemoLeaderboard(Leaderboard):
    """演示用完整实现"""

    def update_score(self, player, new_score):
        if player in self.players:
            old_score = self.players[player]
            if old_score == new_score:
                return
            self.scores.delete(old_score)
        self.scores.insert(new_score, player)
        self.players[player] = new_score

    def get_rank(self, player):
        score = self.players.get(player)
        if score is None:
            return -1
        return self.scores.get_rank(score)
