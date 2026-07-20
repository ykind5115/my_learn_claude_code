# s26-02: 文件操作与权限

[← 返回概览](../README.md) | [上一章：文件系统](../s01_filesystem/) | [下一章：管道与重定向](../s03_pipes_redirect/)

> *"为什么 `Permission denied`？rwx 是什么意思？chmod 755 又是啥？"*

---

## 问题 — 你想读一个文件，系统说"No"

```bash
cat /etc/shadow
# cat: /etc/shadow: Permission denied
```

为什么有些文件你能看，有些不能？因为 Linux 有一个简单但精确的权限系统。

---

## 原理：每个文件有三个"谁"和三个"能做什么"

```
  谁 (Who)              能做什么 (What)
─────────────        ─────────────────
  u (user/属主)         r (read/读)   = 4
  g (group/属组)        w (write/写)  = 2
  o (other/其他人)      x (execute/执行) = 1
```

`ls -l` 看到的权限字符串：

```
-rwxr-xr--  1 alice  dev  1024  Jul 20 10:00  script.sh
 ┬ ┬ ┬
 │ │ └── other: r-- (其他人只能读)
 │ └──── group: r-x (组内人可以读+执行)
 └────── user:  rwx (属主可以读+写+执行)
```

第一个字符 `-` 表示普通文件，`d` 是目录，`l` 是符号链接。

### 数字权限

| 数字 | 权限 | 含义 |
|------|------|------|
| 7 | rwx | 读+写+执行 |
| 6 | rw- | 读+写 |
| 5 | r-x | 读+执行 |
| 4 | r-- | 只读 |
| 0 | --- | 没权限 |

`chmod 755 script.sh` = `rwxr-xr-x`（属主全权限，其他人读+执行）

---

## 核心概念

### 目录的"执行"权限很特殊

- 目录的 `r` = 能看到目录里有哪些文件（`ls`）
- 目录的 `x` = 能**进入**这个目录（`cd`）——即使你不知道里面有什么

```bash
chmod 600 mydir   # rw------- → 属主能读写，但进不去！（没有 x）
cd mydir           # Permission denied
```

### inode — 文件背后的"身份证"

每个文件都有一个 inode（索引节点），存储文件的元数据：
- 权限（rwx）、属主、大小、时间戳
- 数据块在磁盘上的位置

文件名只是指向 inode 的标签。硬链接就是多个文件名指向同一个 inode。

---

## 试一下

```bash
python s26_linux/s02_file_ops/code.py
```

---

## 小结

```
权限 = 谁(ugo) × 做什么(rwx)

r=4  w=2  x=1
chmod 755 = rwxr-xr-x

目录 x = 能 cd 进去
目录 r = 能 ls 看到内容
```
