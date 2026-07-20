# s26-08: 文本处理

[← 返回概览](../README.md) | [上一章：Shell 脚本](../s07_shell_scripting/) | [下一章：包管理](../s09_package_mgmt/)

> *"grep、sed、awk — Linux 的文本处理三剑客。Agent 排查日志时天天用。"*

---

## 问题 — 一个 500MB 的日志文件，你想找所有 ERROR 行

```bash
# 手动打开？不可能——太大了
# 你需要 grep
grep "ERROR" /var/log/app.log
```

---

## 核心概念

### grep — 搜索文本

```bash
grep "ERROR" app.log           # 找含 ERROR 的行
grep -i "error" app.log        # 忽略大小写
grep -v "DEBUG" app.log        # 排除含 DEBUG 的行
grep -c "ERROR" app.log        # 计数
grep -r "TODO" ~/project/      # 递归搜索整个目录
```

### sed — 流编辑器（替换、删除、插入）

```bash
sed 's/old/new/g' file.txt      # 替换（s = substitute, g = global）
sed '/DEBUG/d' app.log           # 删除含 DEBUG 的行
sed -n '10,20p' file.txt         # 只打印第 10-20 行
```

### awk — 列处理器

```bash
awk '{print $1}' access.log      # 打印第一列
awk '{print $1, $NF}' data.txt   # 打印第一列和最后一列
awk '$3 > 100' data.txt          # 第三列 > 100 的行
awk '{sum+=$1} END {print sum}'  # 第一列求和
```

### 三剑客组合使用

```bash
# 找所有 500 错误，提取 IP，去重排序
grep " 500 " access.log | awk '{print $1}' | sort | uniq -c | sort -rn
```

---

## 试一下

```bash
python s26_linux/s08_text_processing/code.py
```

---

## 小结

```
grep    搜索文本 (筛选行)
sed     流编辑 (替换、删除)
awk     列处理 (提取、统计)
|       组合使用 (传送带串联)
```
