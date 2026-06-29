#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini Message Queue — 队列 + 生产者消费者

消息队列是现代分布式系统的核心组件。

═══════════════════════════════════════════════════════════════
核心思想:

  生产者 (Producer)  →  [Queue]  →  消费者 (Consumer)
  发布消息                排队         处理消息

  队列在这里的作用:
    1. 解耦: 生产者和消费者不需要知道对方
    2. 削峰: 生产者快、消费者慢时，消息在队列中排队
    3. 顺序保证: FIFO → 先发布的消息先被处理

═══════════════════════════════════════════════════════════════
你的任务: 实现 MessageQueue 类中标记为 TODO 的方法
"""

import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from s03_mini_mq.queue import Queue


class Message:
    """一条消息"""
    def __init__(self, id, topic, body, retries=0):
        self.id = id
        self.topic = topic
        self.body = body
        self.retries = retries
        self.max_retries = 3

    def can_retry(self):
        return self.retries < self.max_retries

    def __repr__(self):
        return f"Msg({self.id}, topic={self.topic}, body={self.body!r})"


class MessageQueue:
    """迷你消息队列"""

    def __init__(self):
        self.queues = {}          # topic → Queue
        self.dead_letter = Queue()  # 死信队列(处理失败的消息)
        self._msg_counter = 0

    def create_topic(self, topic):
        """创建主题 — 每个主题是一个独立的队列"""
        if topic not in self.queues:
            self.queues[topic] = Queue()

    def publish(self, topic, body):
        """
        发布消息到指定主题。

        提示:
          1. 如果 topic 不存在，先创建
          2. 创建 Message 对象，enqueue 到对应队列
          3. 返回消息 ID
        """
        # TODO: 实现发布消息
        raise NotImplementedError("TODO: 实现 publish")

    def consume(self, topic):
        """
        从指定主题消费一条消息 (FIFO)。
        消费失败的消息进入死信队列 (如果还能重试)。

        返回: Message 对象，或 None (队列为空)
        """
        # TODO: 实现消费消息
        raise NotImplementedError("TODO: 实现 consume")

    def retry(self, message):
        """重试失败的消息 (重新入队)"""
        if message.can_retry():
            message.retries += 1
            self.queues[message.topic].enqueue(message)
            return True
        else:
            self.dead_letter.enqueue(message)
            return False

    def status(self):
        """显示当前状态"""
        print(f"\n  消息队列状态:")
        for topic, q in self.queues.items():
            print(f"    [{topic}] {len(q)} 条消息待处理")
        print(f"    [死信队列] {len(self.dead_letter)} 条")


class DemoMessageQueue(MessageQueue):
    """演示用完整实现"""

    def publish(self, topic, body):
        if topic not in self.queues:
            self.create_topic(topic)
        self._msg_counter += 1
        msg = Message(self._msg_counter, topic, body)
        self.queues[topic].enqueue(msg)
        print(f"    发布: {msg}")
        return msg.id

    def consume(self, topic):
        if topic not in self.queues or self.queues[topic].is_empty():
            return None
        msg = self.queues[topic].dequeue()
        print(f"    消费: {msg}")
        return msg
