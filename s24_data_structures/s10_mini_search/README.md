# s10: Mini Search Engine — 倒排索引

> *"搜索引擎不扫描文档。它提前建好了一张表：哪个词出现在哪些文档里。查询时直接查表——这就是倒排索引。"*
>
> **前提知识**: 学过 s05（哈希表）。理解 O(1) 查找和 O(n) 扫描的区别。

---

## 1. 本章工程问题

你在做一个文档搜索功能。有 100 万篇文档，用户输入「Python tutorial」，找出包含这些词的文档。

### 朴素方案：顺序扫描

```python
def search(query, documents):
    results = []
    for doc in documents:          # 100 万次循环
        if "Python" in doc and "tutorial" in doc:
            results.append(doc)
    return results
```

每次搜索扫描全部 100 万文档 → O(n)。用户等 5 秒？不可接受。

### 更好的方案：提前建索引

就像书的索引页——你不用翻遍整本书找「第 3 章」，直接查索引页，它告诉你「第 3 章在 42 页」。

**搜索引擎也是这个思路**——提前建好「词 → 文档列表」的映射。查询时直接查表。

---

## 2. 正排 vs 倒排：视角的翻转

### 正排索引（文档 → 词）

```
doc1: "Python is great"       → [python, is, great]
doc2: "Python tutorial"       → [python, tutorial]
doc3: "Java tutorial"         → [java, tutorial]
```

给定一篇文档，告诉你里面有什么词。这是「正向」的视角。

### 倒排索引（词 → 文档）

```
"python"    → [doc1, doc2]
"tutorial"  → [doc2, doc3]
"java"      → [doc3]
"great"     → [doc1]
```

给定一个词，告诉你在哪些文档里出现。**视角反过来——所以叫「倒排」。**

---

## 3. 搜索就是集合操作

有了倒排索引，搜索就变成了集合操作：

### AND 查询（所有词都匹配）

```
搜索 "python tutorial":

  "python"  → {doc1, doc2}
  "tutorial" → {doc2, doc3}
  
  AND = {doc1, doc2} ∩ {doc2, doc3} = {doc2}
  
  返回: doc2（唯一同时包含两个词的文档）
```

### OR 查询（任一匹配）

```
搜索 "python java":

  "python" → {doc1, doc2}
  "java"   → {doc3}
  
  OR = {doc1, doc2} ∪ {doc3} = {doc1, doc2, doc3}
```

### NOT 查询

```
搜索 "python NOT tutorial":

  "python"   → {doc1, doc2}
  "tutorial" → {doc2, doc3}
  
  NOT = {doc1, doc2} - {doc2, doc3} = {doc1}
```

---

## 4. 数据结构设计

### 倒排索引 = 哈希表 + 有序列表

```python
{
    # 哈希表: token → posting list（有序的文档 ID 列表）
    "python":    [1, 2, 4, 7, ...],   # 包含 "python" 的文档 ID
    "tutorial":  [2, 3, 5, ...],      # 包含 "tutorial" 的文档 ID
    "java":      [3, 4, 8, ...],
    ...
}
```

**哈希表**：O(1) 查到一个词对应的 posting list。
**有序列表**：posting list 保持文档 ID 有序——AND/OR 操作可以用归并算法（O(m+n)），比哈希表交集更高效。

### Posting List 为什么有序？

```
AND: [1,2,4,7,9] ∩ [2,3,4,8,9]

归并算法（两个指针）:
  p1=0 (1), p2=0 (2): 1<2 → p1++
  p1=1 (2), p2=0 (2): 2=2 → 收集2, p1++, p2++
  p1=2 (4), p2=1 (3): 4>3 → p2++
  p1=2 (4), p2=2 (4): 4=4 → 收集4, p1++, p2++
  ...

时间复杂度: O(len(list1) + len(list2))
```

---

## 5. Python 从零实现

打开 `inverted_index.py`，核心代码：

### 建索引

```python
class InvertedIndex:
    def __init__(self):
        self.index = {}       # token → [doc_ids]
        self.documents = {}   # doc_id → 原始文档

    def add_document(self, doc_id, text):
        self.documents[doc_id] = text
        tokens = set(self.tokenize(text))  # 去重
        
        for token in tokens:
            if token not in self.index:
                self.index[token] = []
            posting = self.index[token]
            # 保持有序（因为 doc_id 递增，直接 append 即可）
            posting.append(doc_id)
```

### AND 查询

```python
def search_and(self, query_text):
    tokens = self.tokenize(query_text)
    if not tokens:
        return []
    
    # 优化：从最短的 posting list 开始
    tokens.sort(key=lambda t: len(self.index.get(t, [])))
    
    result = set(self.index.get(tokens[0], []))
    for token in tokens[1:]:
        result &= set(self.index.get(token, []))
        if not result:
            break  # 交集为空，提前结束
    return sorted(result)
```

### 优化技巧：从最短的 posting list 开始

```
"the python tutorial"

"the"  → [1,2,3,4,5,...,1000000]  ← 100 万个文档！
"python" → [2, 5]                   ← 只有 2 个
"tutorial" → [2, 3, 7]              ← 3 个

如果从 "the" 开始 → 要在 100 万的集合上做交集
如果从 "python" 开始 → 只需要在 2 个元素上检查 → 快得多！
```

---

## 6. 时间复杂度分析

| 操作 | 复杂度 | 解释 |
|------|--------|------|
| `add_document()` | O(n) | n = 文档中的唯一 token 数 |
| `search_and()` | O(k × m) | k = 查询词数, m = 平均 posting list 长度 |
| `search_or()` | O(k × m) | 同上 |

对比顺序扫描的 O(n)（n = 文档总数）——倒排索引把复杂度从「依赖文档总数」变成了「依赖查询词数和匹配文档数」。这在 n 很大、m 很小时是巨大的提升。

---

## 7. 小型项目实践

### Mini Search Engine

本章没有独立的 Mini 框架文件——倒排索引本身就是搜索引擎的「引擎」。你需要做的：

1. 读懂 `inverted_index.py`（重点是 `add_document` 和 `search_and`）
2. 自己创建 `mini_search.py`——包含：
   - `SearchEngine` 类，封装 `InvertedIndex`
   - 支持 `add_document()`, `search()`, `advanced_search()`（支持 AND/OR/NOT）
3. 用一批真实文档做测试（比如维基百科文章）

---

## 8. 可视化运行过程

运行 `python s24_data_structures/s10_mini_search/code.py`：

```
步骤 1: 正排 vs 倒排
  正排: 文档 → 词列表
  倒排: 词 → 文档列表（箭头反过来）

步骤 2: 建索引
  索引中的 posting list:
    'python'     → doc[1, 2, 4]
    'programming' → doc[1, 3, 5]
    'tutorial'   → doc[2, 3]

步骤 3: 搜索 'python programming' (AND)
  → doc[1] ("Python is a great programming language")

步骤 4: 搜索 'rust java' (OR)
  → doc[3, 4, 5]
```

---

## 9. 思考题

1. **为什么 posting list 要保持有序？** 如果 posting list 无序，AND 查询怎么做？复杂度会变成多少？

2. **倒排索引的空间开销有多大？** 假设 100 万文档，平均每个文档 500 个唯一词，总共需要存储多少 posting 条目？和原始文档大小比怎么样？

3. **Elasticsearch 在这个基础上加了什么？** 分布式（索引分片）、相关性排序（TF-IDF/BM25）、实时索引——这些分别解决了什么问题？

4. **中文分词和英文有什么不同？** 英文按空格分词即可，中文没有空格——「我爱北京天安门」怎么分词？这对倒排索引有什么影响？

5. **自己实现 `mini_search.py`**：如果用户输入 `"python" -"java"`（包含 python 但不包含 java），你的 search 方法怎么处理这个 NOT 逻辑？

---

## 10. 本章总结

| 概念 | 一句话 |
|------|--------|
| 正排索引 | 文档 → 词列表：给定文档，看有什么词 |
| 倒排索引 | 词 → 文档列表：给定词，看哪些文档有它 |
| Posting List | 包含某个词的所有文档 ID 列表（有序） |
| AND 查询 | 所有 token 的 posting list 做交集 |
| OR 查询 | 所有 token 的 posting list 做并集 |
| 优化 | 从最短的 posting list 开始做交集 |

> **核心收获**：倒排索引 = 哈希表（O(1) 定位 posting list）+ 有序列表（高效集合操作）。搜索引擎的「毫秒级响应」不是魔法——它只是提前把「词→文档」的映射算好了。查询时不需要扫描文档，只需要操作 posting list。

---

**上一章**: [s09: Mini DB Index — B+ 树](../s09_mini_db_index/)
**下一章**: [s11: Mini Agent Framework — 图 + DAG](../s11_mini_agent/)
