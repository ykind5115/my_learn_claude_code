#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s00-07: Shell、JSON、YAML — Agent 的语言和工具

学习目标:
  - 执行 shell 命令和管道
  - JSON 序列化/反序列化
  - JSON Schema 验证
  - YAML 读写

运行: python 07_shell_json/code.py
"""

import os
import sys
import json
import subprocess


# ═══════════════════════════════════════════════════════════
# Demo 1: Shell 命令执行
# ═══════════════════════════════════════════════════════════
def demo_1_shell():
    print("── Demo 1: Shell 命令 ──")

    # 基本命令
    r = subprocess.run(["echo", "Hello from Python!"],
                       capture_output=True, text=True)
    print(f"  echo → {r.stdout.strip()}")

    # 管道效果：用 Python 模拟
    r1 = subprocess.run(["echo", "line1\nline2\nerror line\nline3"],
                        capture_output=True, text=True)
    # 把 stdout 传给 grep 的 stdin
    r2 = subprocess.run(
        ["grep", "error"],
        input=r1.stdout,
        capture_output=True, text=True,
    )
    print(f"  echo ... | grep error → {r2.stdout.strip()}")
    print(f"  → Python 里 input 参数 = 管道的 stdin")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 2: JSON 基本操作
# ═══════════════════════════════════════════════════════════
def demo_2_json():
    print("── Demo 2: JSON ──")

    # Python dict → JSON 字符串
    data = {
        "name": "bash",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"}
            },
            "required": ["command"]
        }
    }
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    print("  Python dict → JSON:")
    print(f"  {json_str}")

    # JSON 字符串 → Python dict
    parsed = json.loads('{"model": "claude-sonnet-5", "max_tokens": 8000}')
    print(f"  JSON → Python: {parsed}")
    print(f"  parsed['model'] = {parsed['model']}")

    # JSON 的六种类型
    print("  JSON 六种类型: string, number, boolean, null, object, array")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 3: JSON Schema 验证
# ═══════════════════════════════════════════════════════════
def demo_3_json_schema():
    print("── Demo 3: JSON Schema 验证 ──")

    # 模拟工具定义的 schema
    tool_schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string"},
            "timeout": {"type": "integer", "minimum": 1},
        },
        "required": ["command"]
    }

    # 简单的 schema 验证器
    def validate(schema, data):
        errors = []
        # 检查 required
        for field in schema.get("required", []):
            if field not in data:
                errors.append(f"缺少必填字段: {field}")
        # 检查类型
        for field, rules in schema.get("properties", {}).items():
            if field in data:
                expected = rules["type"]
                actual = type(data[field]).__name__
                if expected == "integer" and not isinstance(data[field], int):
                    errors.append(f"{field}: 期望 {expected}, 实际 {actual}")
                elif expected == "string" and not isinstance(data[field], str):
                    errors.append(f"{field}: 期望 {expected}, 实际 {actual}")
        return errors

    # 正确数据
    good = {"command": "ls -la", "timeout": 30}
    print(f"  正确输入: {good}")
    print(f"  验证结果: {validate(tool_schema, good)} ✓")

    # 错误数据：缺少必填字段
    bad1 = {"timeout": 30}
    print(f"  缺少 command: {bad1}")
    print(f"  验证结果: {validate(tool_schema, bad1)}")

    # 错误数据：类型不对
    bad2 = {"command": 123}
    print(f"  command 不是 string: {bad2}")
    print(f"  验证结果: {validate(tool_schema, bad2)}")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 4: YAML 基本操作
# ═══════════════════════════════════════════════════════════
def demo_4_yaml():
    print("── Demo 4: YAML ──")

    try:
        import yaml

        # dict → YAML
        data = {
            "name": "my-skill",
            "version": "1.0",
            "description": "A demo skill",
            "steps": [
                {"name": "step1", "command": "echo hello"},
                {"name": "step2", "command": "echo world"},
            ]
        }
        yaml_str = yaml.dump(data, allow_unicode=True, default_flow_style=False)
        print(f"  Python dict → YAML:")
        for line in yaml_str.strip().split("\n"):
            print(f"    {line}")

        # YAML → dict
        yaml_input = """
name: read-file
description: Read a file from disk
parameters:
  path:
    type: string
    required: true
"""
        parsed = yaml.safe_load(yaml_input)
        print(f"\n  YAML → Python: {parsed}")
        print(f"  parsed['name'] = {parsed['name']}")

    except ImportError:
        print("  PyYAML 未安装。安装: pip install pyyaml")
        print("  模拟 YAML 的简洁性:")
        print("    JSON:  {\"name\": \"bash\", \"params\": {\"cmd\": \"ls\"}}")
        print("    YAML:  name: bash")
        print("           params:")
        print("             cmd: ls")
        print("    → YAML 用缩进代替大括号，适合手写")
    print()


# ═══════════════════════════════════════════════════════════
# Demo 5: 模拟 Agent 的工具调用
# ═══════════════════════════════════════════════════════════
def demo_5_agent_tool_call():
    print("── Demo 5: 模拟 Agent 的工具调用流程 ──")

    # 模型返回的 JSON（tool_use 块）
    model_response = """
    {
      "tool_use": [
        {
          "id": "call_001",
          "name": "bash",
          "input": {"command": "ls -la"}
        },
        {
          "id": "call_002",
          "name": "read",
          "input": {"file_path": "README.md"}
        }
      ]
    }
    """
    parsed = json.loads(model_response)
    print(f"  模型返回的 tool_use 块:")
    for call in parsed["tool_use"]:
        print(f"    id={call['id']}, tool={call['name']}, args={call['input']}")

    # 执行工具
    print()
    print(f"  执行 call_001 (bash):")
    r = subprocess.run(["ls", "-la"],
                       capture_output=True, text=True)
    result = {
        "type": "tool_result",
        "tool_use_id": "call_001",
        "content": r.stdout[:200],
    }
    print(f"    结果: {json.dumps(result, indent=2, ensure_ascii=False)[:150]}...")
    print(f"    → 这个 JSON 会追加到 messages 数组喂回模型")
    print()


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("s00-07: Shell、JSON、YAML — Agent 的语言")
    print("=" * 60)
    print()

    demo_1_shell()
    demo_2_json()
    demo_3_json_schema()
    demo_4_yaml()
    demo_5_agent_tool_call()

    print("─" * 60)
    print("小结:")
    print("  Shell: bash 命令, | 管道, > 重定向")
    print("  JSON: 六种类型, API 通信和工具定义的通用语")
    print("  JSON Schema: 验证 JSON 的结构和类型")
    print("  YAML: 缩进代替大括号, 适合人写配置文件")
