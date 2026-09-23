#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""企业知识助手（最小练习版）——云帆科技虚构数据。

完全离线，仅使用 Python 标准库。
核心设计：检索前先按角色做权限过滤，无权限的文档不会进入候选集。

对应学习工作台阶段：s2（数据审计：manifest.json 即文档清单 + 权限矩阵）、
s3（检索基线：可重建索引 + 带权限过滤的检索接口 + 测试问题）。
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent / "kb_docs"
MANIFEST = "manifest.json"

# 角色 → 可见敏感级（权限矩阵的最小实现）
ROLE_VISIBILITY = {
    "intern": {"public"},
    "all_staff": {"public", "internal"},
    "hr_admin": {"public", "internal", "confidential"},
}

_CJK = re.compile(r"[\u4e00-\u9fff]")
_LATIN = re.compile(r"[a-z0-9]+")


def tokenize(text):
    """极简分词：连续拉丁字符/数字按词，其余按中文二字组（bigram）。"""
    tokens = []
    for m in _LATIN.finditer(text.lower()):
        tokens.append(m.group(0))
    cjk = "".join(ch for ch in text if _CJK.match(ch))
    tokens.extend(cjk[i : i + 2] for i in range(len(cjk) - 1))
    return tokens


def load_manifest(docs_dir=DOCS_DIR):
    with open(Path(docs_dir) / MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def permitted_ids(manifest, role):
    """权限过滤：返回该角色可见的文档 id 集合。未知角色直接报错。"""
    if role not in ROLE_VISIBILITY:
        raise ValueError(f"未知角色: {role}（可选：{' / '.join(ROLE_VISIBILITY)}）")
    visible = ROLE_VISIBILITY[role]
    return {d["id"] for d in manifest["docs"] if d["sensitivity"] in visible}


def build_index(docs_dir=DOCS_DIR):
    """构建内存索引（可重复调用，幂等）：doc_id -> {meta, tokens, text}。"""
    docs_dir = Path(docs_dir)
    manifest = load_manifest(docs_dir)
    index = {}
    for doc in manifest["docs"]:
        text = (docs_dir / doc["file"]).read_text(encoding="utf-8")
        index[doc["id"]] = {
            "meta": doc,
            "text": text,
            "tokens": Counter(tokenize(doc["title"] + "\n" + text)),
        }
    return index


def _snippet(text, query_tokens, width=60):
    pos = min((text.find(t) for t in query_tokens if len(t) >= 2 and text.find(t) >= 0), default=-1)
    if pos < 0:
        return text[:width].replace("\n", " ")
    start = max(0, pos - width // 3)
    return text[start : start + width].replace("\n", " ")


def retrieve(index, manifest, role, question, top_k=3):
    """带权限过滤的检索：先按角色过滤候选集，再对候选打分排序。"""
    allowed = permitted_ids(manifest, role)  # 1. 权限过滤（在检索之前）
    q_tokens = set(tokenize(question))
    scored = []
    for doc_id in sorted(allowed):  # 2. 只在有权限的候选集内检索
        entry = index[doc_id]
        score = sum(entry["tokens"].get(t, 0) for t in q_tokens)
        score += 3 * sum(entry["tokens"].get(t, 0) for t in q_tokens & set(tokenize(entry["meta"]["title"])))
        if score > 0:
            scored.append((score, doc_id))
    scored.sort(key=lambda x: (-x[0], x[1]))
    results = []
    for score, doc_id in scored[:top_k]:
        entry = index[doc_id]
        results.append({
            "doc_id": doc_id,
            "title": entry["meta"]["title"],
            "score": score,
            "snippet": _snippet(entry["text"], list(q_tokens)),
        })
    return results


def answer(index, manifest, role, question, top_k=3):
    """最小回答：返回带引用的摘录拼接；无依据时拒答。"""
    results = retrieve(index, manifest, role, question, top_k=top_k)
    if not results:
        return {
            "refused": True,
            "answer": "抱歉，我在您有权访问的资料中没有找到足够依据，无法回答这个问题。"
                      "建议联系对应文档维护人确认。",
            "citations": [],
        }
    parts = []
    citations = []
    for r in results:
        citations.append({"doc_id": r["doc_id"], "title": r["title"]})
        parts.append(f"根据《{r['title']}》（{r['doc_id']}）：{r['snippet']}……")
    return {"refused": False, "answer": "\n".join(parts), "citations": citations}


def main(argv=None):
    parser = argparse.ArgumentParser(description="企业知识助手（虚构数据练习版）")
    parser.add_argument("--role", default="all_staff", help="角色：intern / all_staff / hr_admin")
    parser.add_argument("--question", help="提问（中文）")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--list-docs", action="store_true", help="列出当前角色可见的文档")
    args = parser.parse_args(argv)

    manifest = load_manifest()
    index = build_index()

    if args.list_docs:
        allowed = permitted_ids(manifest, args.role)
        role_name = manifest["roles"].get(args.role, {}).get("name", args.role)
        hidden = len(manifest["docs"]) - len(allowed)
        print(f"角色：{args.role}（{role_name}），可见 {len(allowed)} 份文档：")
        for d in manifest["docs"]:
            if d["id"] in allowed:  # 无权限文档不显示编号/标题/敏感级，避免元数据泄露
                print(f"  {d['id']} 《{d['title']}》 [{d['sensitivity']}]")
        if hidden:
            print(f"  …另有 {hidden} 份文档因权限不可见（不显示编号、标题与敏感级）")
        return 0

    if not args.question:
        parser.error("请提供 --question，或使用 --list-docs")

    result = answer(index, manifest, args.role, args.question, top_k=args.top_k)
    print(f"角色：{args.role}　问题：{args.question}\n")
    print(result["answer"])
    if result["citations"]:
        print("\n引用：" + "、".join(f"《{c['title']}》({c['doc_id']})" for c in result["citations"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
