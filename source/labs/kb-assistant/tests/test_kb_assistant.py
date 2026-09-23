#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""企业知识助手最小练习的测试集（unittest，仅标准库）。

运行：cd labs/kb-assistant && python3 -m unittest discover -s tests -v
"""

import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import kb_assistant as kb  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


class TestPermissionFilter(unittest.TestCase):
    """权限过滤：检索前按角色裁剪候选集（对应 s2 权限矩阵 / s3 越权用例）。"""

    def setUp(self):
        self.manifest = kb.load_manifest()
        self.index = kb.build_index()

    def test_role_visibility_escalates(self):
        intern = kb.permitted_ids(self.manifest, "intern")
        staff = kb.permitted_ids(self.manifest, "all_staff")
        hr = kb.permitted_ids(self.manifest, "hr_admin")
        self.assertEqual(len(intern), 5)      # public 5 份
        self.assertEqual(len(staff), 9)       # public + internal
        self.assertEqual(len(hr), 12)         # 全部
        self.assertTrue(intern < staff < hr)

    def test_unknown_role_rejected(self):
        with self.assertRaises(ValueError):
            kb.permitted_ids(self.manifest, "ceo")

    def test_intern_cannot_retrieve_confidential(self):
        results = kb.retrieve(self.index, self.manifest, "intern", "薪酬带宽是多少", top_k=10)
        ids = {r["doc_id"] for r in results}
        self.assertNotIn("D010", ids)
        self.assertNotIn("D011", ids)

    def test_intern_cannot_retrieve_internal(self):
        results = kb.retrieve(self.index, self.manifest, "intern", "销售佣金怎么计提", top_k=10)
        self.assertNotIn("D007", {r["doc_id"] for r in results})

    def test_results_within_permitted_set(self):
        for role in ("intern", "all_staff", "hr_admin"):
            allowed = kb.permitted_ids(self.manifest, role)
            results = kb.retrieve(self.index, self.manifest, role, "公司 制度 流程", top_k=12)
            self.assertTrue({r["doc_id"] for r in results} <= allowed, role)


class TestRetrieval(unittest.TestCase):
    """检索基线：命中预期来源、拒答、引用可回溯（对应 s3）。"""

    def setUp(self):
        self.manifest = kb.load_manifest()
        self.index = kb.build_index()

    def test_build_index_covers_all_docs(self):
        self.assertEqual(set(self.index), {d["id"] for d in self.manifest["docs"]})

    def test_build_index_is_repeatable(self):
        again = kb.build_index()
        self.assertEqual(again.keys(), self.index.keys())

    def test_question_hits_expected_doc(self):
        results = kb.retrieve(self.index, self.manifest, "all_staff", "年假有几天")
        self.assertTrue(results, "应至少有一条结果")
        self.assertEqual(results[0]["doc_id"], "D001")

    def test_hr_gets_confidential_doc(self):
        results = kb.retrieve(self.index, self.manifest, "hr_admin", "年终奖怎么算")
        self.assertEqual(results[0]["doc_id"], "D011")

    def test_unknown_question_refused(self):
        result = kb.answer(self.index, self.manifest, "all_staff", "食堂中午几点开饭")
        self.assertTrue(result["refused"])
        self.assertEqual(result["citations"], [])

    def test_citations_traceable(self):
        result = kb.answer(self.index, self.manifest, "all_staff", "报销时限是多久")
        self.assertFalse(result["refused"])
        ids = {d["id"] for d in self.manifest["docs"]}
        for c in result["citations"]:
            self.assertIn(c["doc_id"], ids)


class TestCli(unittest.TestCase):
    """命令行冒烟测试：退出码与关键输出。"""

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "kb_assistant.py"), *args],
            capture_output=True, text=True, timeout=30,
        )

    def test_cli_list_docs(self):
        proc = self.run_cli("--role", "intern", "--list-docs")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        # 可见文档正常列出
        self.assertIn("D001", proc.stdout)
        self.assertIn("考勤与假期制度", proc.stdout)
        # 无权限文档的元数据（编号/标题/文件名/敏感级）一律不得泄露
        for leaked in ("D010", "D011", "D012", "薪酬带宽", "年终奖分配细则",
                       "星桥数据", "confidential"):
            self.assertNotIn(leaked, proc.stdout)
        # 只允许透露隐藏文档的数量
        self.assertIn("7 份", proc.stdout)

    def test_cli_list_docs_hr_sees_confidential(self):
        # HR 管理员对机密文档有权限，因此可以正常看到其元数据
        proc = self.run_cli("--role", "hr_admin", "--list-docs")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("D010", proc.stdout)
        self.assertIn("薪酬带宽", proc.stdout)

    def test_cli_answer_refusal(self):
        proc = self.run_cli("--role", "intern", "--question", "食堂中午几点开饭")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("无法回答", proc.stdout)


if __name__ == "__main__":
    unittest.main()
