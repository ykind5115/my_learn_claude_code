# s26-09: 包管理

[← 返回概览](../README.md) | [上一章：文本处理](../s08_text_processing/) | [下一章：SSH 远程](../s10_ssh_remote/)

> *"apt install 背后发生了什么？依赖是怎么解决的？pip 和 apt 有什么区别？"*

---

## 问题 — 你想装一个包，但系统说依赖冲突

```bash
pip install some-package
# ERROR: some-package 3.0 requires other-lib>=2.0,
# but you have other-lib 1.5 installed.
```

包管理器的核心工作就是解决依赖。

---

## 核心概念

### 系统包管理器 vs 语言包管理器

| | apt (Debian/Ubuntu) | pip (Python) | npm (Node.js) |
|---|---|---|---|
| 管什么 | 系统软件（python、git、nginx） | Python 库 | JS 库 |
| 安装位置 | `/usr/bin/`, `/usr/lib/` | `venv/lib/site-packages/` | `node_modules/` |
| 依赖解决 | 自动 | 自动 | 自动 |
| 版本锁定 | `apt-mark hold` | `requirements.txt` + `==` | `package-lock.json` |

### apt 常用命令

```bash
apt update              # 更新软件源列表
apt install nginx       # 安装
apt remove nginx        # 卸载（保留配置）
apt purge nginx         # 卸载（连配置一起删）
apt search keyword      # 搜索
apt list --installed    # 查看已安装
```

### pip 常用命令

```bash
pip install package              # 安装
pip install package==1.2.3       # 指定版本
pip install -r requirements.txt  # 批量安装
pip freeze > requirements.txt    # 导出当前环境
pip list                         # 查看已安装
```

### 虚拟环境 — 隔离是关键

```bash
python -m venv myenv       # 创建虚拟环境
source myenv/bin/activate  # 激活（Linux/macOS）
myenv\Scripts\activate     # 激活（Windows）
pip install xxx            # 只安装在这个环境里
deactivate                 # 退出
```

---

## 试一下

```bash
python s26_linux/s09_package_mgmt/code.py
```

---

## 小结

```
apt    系统级包管理器 (装 git, nginx, python)
pip    语言级包管理器 (装 Python 库)
venv   虚拟环境 → 每个项目独立的 Python 包
依赖   包管理器自动解决，版本号用 ==1.2.3 锁定
```
