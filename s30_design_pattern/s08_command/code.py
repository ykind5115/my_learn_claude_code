#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s30-08: 命令模式"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Color, print_step, print_note, print_key_point, print_section, print_agent_link
from abc import ABC, abstractmethod

class TextEditor:
    def __init__(self):
        self.text = ""
    def insert(self, pos, s):
        self.text = self.text[:pos] + s + self.text[pos:]
    def delete(self, pos, length):
        self.text = self.text[:pos] + self.text[pos+length:]

class Command(ABC):
    @abstractmethod
    def execute(self): pass
    @abstractmethod
    def undo(self): pass

class InsertCommand(Command):
    def __init__(self, editor, text, pos):
        self.editor = editor; self.text = text; self.pos = pos
    def execute(self):
        self.editor.insert(self.pos, self.text)
    def undo(self):
        self.editor.delete(self.pos, len(self.text))

class DeleteCommand(Command):
    def __init__(self, editor, pos, length):
        self.editor = editor; self.pos = pos; self.length = length
        self.deleted = ""
    def execute(self):
        self.deleted = self.editor.text[self.pos:self.pos+self.length]
        self.editor.delete(self.pos, self.length)
    def undo(self):
        self.editor.insert(self.pos, self.deleted)

class CommandHistory:
    def __init__(self):
        self.history = []; self.redo_stack = []
    def execute(self, cmd):
        cmd.execute(); self.history.append(cmd); self.redo_stack.clear()
    def undo(self):
        if self.history:
            cmd = self.history.pop(); cmd.undo(); self.redo_stack.append(cmd)

def demo_all():
    print_step(1, "命令模式: 文本编辑器 + Undo")
    editor = TextEditor()
    history = CommandHistory()

    history.execute(InsertCommand(editor, "Hello", 0))
    print(f"  插入 'Hello': '{editor.text}'")
    history.execute(InsertCommand(editor, " World", 5))
    print(f"  插入 ' World': '{editor.text}'")

    history.undo()
    print(f"  Undo: '{editor.text}'")
    history.undo()
    print(f"  Undo: '{editor.text}'")

    print_agent_link("Command", "s12 Task System", "任务=命令对象, 支持回滚")

if __name__ == "__main__":
    print_section("s30-08: 命令模式")
    demo_all()
    print(f"\n{Color.BOLD}{'-'*60}{Color.RESET}")
    print_key_point("命令 = 操作对象化, 支持 undo/redo/队列")
