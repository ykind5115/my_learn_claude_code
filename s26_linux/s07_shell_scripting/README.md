# s26-07: Shell 脚本基础

[← 返回概览](../README.md) | [上一章：用户与权限](../s06_users_perms/) | [下一章：文本处理](../s08_text_processing/)

> *"怎么把一串命令变成可复用的脚本？怎么让脚本根据条件做不同的事？"*

---

## 问题 — 你每天都要跑这 5 个命令

```bash
cd ~/project
git pull
pip install -r requirements.txt
python train.py
echo "训练完成" | mail -s "通知" me@example.com
```

每次都手敲？写个脚本一次搞定。

---

## 原理：脚本就是"批处理文件"

Shell 脚本 = 一个文本文件，里面放着你平时在终端敲的命令。加一些控制流（if/for/while），就是自动化。

---

## 核心概念

### Shebang — 第一行决定谁执行

```bash
#!/bin/bash
# ↑ 这个叫 shebang（#! = sharp + bang）
# 告诉 OS："用 /bin/bash 来执行这个文件"
```

### 变量

```bash
NAME="world"
echo "Hello, $NAME"     # Hello, world
echo "Hello, ${NAME}"   # Hello, world（花括号明确边界）
```

### 条件判断

```bash
if [ -f "config.yaml" ]; then     # -f = 文件存在？
    echo "配置文件存在"
elif [ -d "logs" ]; then          # -d = 目录存在？
    echo "logs 目录存在"
else
    echo "啥都没有"
fi
```

### 循环

```bash
for file in *.py; do
    echo "检查: $file"
    python -m py_compile "$file"
done
```

### 退出码和 `$?`

```bash
python train.py
if [ $? -eq 0 ]; then    # $? = 上一条命令的退出码
    echo "训练成功"
else
    echo "训练失败！"
fi
```

### 函数

```bash
backup() {
    local src=$1           # local = 函数内部变量
    cp -r "$src" "${src}.bak"
    echo "备份完成: ${src}.bak"
}

backup ~/project
```

---

## 试一下

```bash
python s26_linux/s07_shell_scripting/code.py
```

---

## 小结

```
#!/bin/bash         shebang，告诉 OS 谁执行
$VAR ${VAR}         变量 (双引号里会展开)
if [ -f file ]      文件存在判断
for f in *.py       遍历文件
$?                  上一条命令的退出码
function() {}       函数 (local 限定作用域)
```
