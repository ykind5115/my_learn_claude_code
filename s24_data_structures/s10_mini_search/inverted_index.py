#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
倒排索引 (Inverted Index) — 搜索引擎的核心

正排索引: 文档 → 词列表 (你打开一个文档，看里面有什么词)
倒排索引: 词 → 文档列表 (你输入一个词，看哪些文档包含它)

这就是「倒排」的含义——从「文档找词」变成「词找文档」。

结构:
  Token → Posting List (包含该 token 的文档 ID 列表)

  "python"    → [doc1, doc3, doc7]
  "tutorial"  → [doc2, doc3, doc5]

查询 "python tutorial":
  取 "python" 的 posting list: [1,3,7]
  取 "tutorial" 的 posting list: [2,3,5]
  AND: [3] (文档 3 同时包含两个词)
  OR:  [1,2,3,5,7]

工程应用:
  - Elasticsearch / Lucene
  - Google 搜索引擎
  - GitHub 代码搜索
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import Color


class InvertedIndex:
    """
    倒排索引 — 支持建索引、AND/OR 查询

    底层: dict (哈希表) → posting list (有序列表)
    """

    def __init__(self):
        self.index = {}       # token → [doc_id, ...] (有序)
        self.documents = {}   # doc_id → 原始文档

    # ── 分词 ───────────────────────────────────────────

    def tokenize(self, text):
        """
        简单分词 — 转小写 + 按空格分割 + 去标点

        生产环境中会用到更复杂的分词器 (jieba, nltk)。
        """
        import re
        return re.findall(r'\w+', text.lower())

    # ── 建索引 ─────────────────────────────────────────

    def add_document(self, doc_id, text):
        """
        添加文档并建索引 — O(n) n=文档中的 token 数

        对文档中每个 token，把 doc_id 追加到它的 posting list。
        """
        self.documents[doc_id] = text
        tokens = set(self.tokenize(text))  # 去重 — 一个词在文档中出现多次只记一次

        for token in tokens:
            if token not in self.index:
                self.index[token] = []
            posting = self.index[token]
            # 保持有序插入
            if not posting or posting[-1] < doc_id:
                posting.append(doc_id)

    # ── 搜索 ───────────────────────────────────────────

    def search_and(self, query_text):
        """
        AND 查询 — 所有词都匹配的文档 — O(k × m) k=词数, m=平均 posting list 长度

        用集合交集: 所有 token 的 posting lists 的交集。
        """
        tokens = self.tokenize(query_text)
        if not tokens:
            return []

        # 从最短的 posting list 开始 (优化)
        tokens.sort(key=lambda t: len(self.index.get(t, [])))

        result = set(self.index.get(tokens[0], []))
        for token in tokens[1:]:
            result &= set(self.index.get(token, []))
            if not result:
                break

        return sorted(result)

    def search_or(self, query_text):
        """
        OR 查询 — 任一词匹配的文档 — O(k × m)

        用集合并集。
        """
        tokens = self.tokenize(query_text)
        result = set()
        for token in tokens:
            result |= set(self.index.get(token, []))
        return sorted(result)

    # ── 信息 ───────────────────────────────────────────

    def stats(self):
        """索引统计"""
        total_postings = sum(len(p) for p in self.index.values())
        return {
            "文档数": len(self.documents),
            "唯一词数": len(self.index),
            "平均 posting list 长度": f"{total_postings / max(len(self.index), 1):.1f}",
        }


# ═══════════════════════════════════════════════════════════════
# 演示
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    from utils import print_step, print_key_point, print_note

    print(f"\n{Color.HEADER}  倒排索引 — 搜索引擎核心{Color.RESET}\n")

    idx = InvertedIndex()

    print_step("1", "添加文档并建索引")
    docs = [
        "Python is a great programming language",
        "Python tutorial for beginners",
        "Java programming tutorial",
        "Learn Python and Java",
        "Rust programming language guide",
    ]
    for i, text in enumerate(docs, 1):
        idx.add_document(i, text)
        print_note(f"doc{i}: {text}")

    print_step("2", "AND 查询: 'python tutorial' (两个词都要匹配)")
    results = idx.search_and("python tutorial")
    print_note(f"结果: doc{results} → '{docs[results[0]-1]}'")

    print_step("3", "OR 查询: 'rust guide' (任一匹配即可)")
    results = idx.search_or("rust guide")
    for r in results:
        print_note(f"  doc{r}: {docs[r-1]}")

    print_note(f"\n索引统计: {idx.stats()}")

    print_key_point(
        "倒排索引 = 从「文档→词」变成「词→文档」。\n"
        "    查询时直接取 posting list，不需要扫描文档。\n"
        "    搜索引擎能在毫秒级返回结果的秘密。"
    )
