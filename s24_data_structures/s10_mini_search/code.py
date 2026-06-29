#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s10: Mini Search Engine — 倒排索引

运行: python s24_data_structures/s10_mini_search/code.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (
    Color, print_header, print_step, print_note, print_key_point, print_success,
)
from s10_mini_search.inverted_index import InvertedIndex


def demo():
    print_step(1, "正排 vs 倒排 — 视角的翻转")
    print_note("正排索引: 文档 → 词列表 (打开文档看有什么词)")
    print_note("倒排索引: 词 → 文档列表 (输入词找哪些文档有它)")
    print_note("倒排索引 = 把「正排」的箭头反过来")

    print_step(2, "建索引")
    idx = InvertedIndex()
    docs = [
        "Python is a great programming language",
        "Python tutorial for beginners",
        "Java programming tutorial",
        "Learn Python and Java",
        "Rust programming language guide",
    ]
    for i, text in enumerate(docs, 1):
        idx.add_document(i, text)

    print_note("索引中的 posting list:")
    for token in ["python", "programming", "tutorial", "java", "rust"]:
        print_note(f"  '{token}' → doc{idx.index.get(token, [])}")

    print_step(3, "搜索 'python programming' (AND)")
    results = idx.search_and("python programming")
    print_note(f"包含 'python' 和 'programming' 的文档: doc{results}")
    print_note(f"→ {docs[results[0]-1]}")

    print_step(4, "搜索 'rust java' (OR)")
    results = idx.search_or("rust java")
    for r in results:
        print_note(f"  doc{r}: {docs[r-1]}")

    print_key_point(
        "搜索引擎的「毫秒级响应」靠的就是倒排索引:\n"
        "    不扫描文档，直接查 posting list，取交集/并集。\n"
        "    Elasticsearch 底层就是增强版的倒排索引。"
    )


def main():
    print_header("s10: Mini Search Engine — 倒排索引")
    print(f"  {Color.HIGHLIGHT}数据结构: 倒排索引 = 哈希表 + 有序列表{Color.RESET}\n")
    demo()
    print(f"\n{Color.HEADER}{'═' * 65}{Color.RESET}")
    print(f"\n{Color.SUCCESS}✅ 倒排索引 = 搜索引擎的基石。词→文档的映射。{Color.RESET}\n")


if __name__ == "__main__":
    main()
