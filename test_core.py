import io
import json
import unittest
from unittest.mock import patch

from docx import Document

from core import Passage, _check_public_pdf_url, analyze, normalize_doi, paper_matrix_row, parse_document, search_passages, select_evidence


class LiteratureReaderTests(unittest.TestCase):
    def test_docx_and_chinese_search(self):
        doc = Document()
        doc.add_paragraph("基层治理中的村民自治与行政化张力，可以通过访谈和问卷调查展开分析。")
        target = io.BytesIO()
        doc.save(target)
        passages, warnings = parse_document("研究.docx", target.getvalue())
        self.assertFalse(warnings)
        self.assertEqual(passages[0].locator, "段落 1")
        self.assertEqual(len(search_passages("村民 自治", passages)), 1)
        self.assertTrue(select_evidence("访谈方法", passages))

    def test_eight_papers_represented_in_context(self):
        passages = [Passage(f"paper{i}", f"PDF 第 {page} 页", "基层治理与村民自治研究。" * 60)
                    for i in range(8) for page in range(1, 10)]
        selected = select_evidence("基层治理", passages)
        self.assertEqual({p.document for _, p in selected}, {f"paper{i}" for i in range(8)})

    def test_model_citations_must_match_supplied_evidence(self):
        result = {"choices": [{"message": {"content": json.dumps({
            "claims": [
                {"text": "有问卷", "sources": ["E1", "E999"]},
                {"text": "无出处的说法", "sources": ["E999"]},
            ], "limits": "部分页段"}, ensure_ascii=False)}}]}
        with patch("core._json_request", return_value=result):
            answer = analyze("研究方法", [("E1", Passage("paper", "PDF 第 2 页", "采用问卷"))], "key", "model")
        self.assertEqual(answer["claims"], [{"text": "有问卷", "sources": ["E1"]}])

    def test_matrix_does_not_accept_unverified_fields(self):
        payload = {"研究问题": {"text": "村民自治", "sources": ["E1"]},
                   "数据或样本": {"text": "虚构的样本数", "sources": ["E999"]}}
        result = {"choices": [{"message": {"content": json.dumps(payload, ensure_ascii=False)}}]}
        with patch("core._json_request", return_value=result):
            row = paper_matrix_row("paper", [Passage("paper", "PDF 第 1 页", "研究村民自治的制度安排。")], "key", "model")
        self.assertEqual(row["研究问题_出处"], "PDF 第 1 页")
        self.assertEqual(row["数据或样本"], "未在检索片段中确认")

    def test_doi_and_private_address_rejection(self):
        self.assertEqual(normalize_doi("https://doi.org/10.1234/example"), "10.1234/example")
        with patch("core.socket.getaddrinfo", return_value=[(None, None, None, None, ("127.0.0.1", 443))]):
            with self.assertRaises(ValueError):
                _check_public_pdf_url("https://example.com/file.pdf")


if __name__ == "__main__":
    unittest.main()
