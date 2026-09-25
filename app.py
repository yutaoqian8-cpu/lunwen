"""Streamlit interface. Run with: streamlit run app.py"""

import csv
import hashlib
import io
import os

import streamlit as st

from core import MATRIX_FIELDS, Passage, analyze, open_pdf_by_doi, paper_matrix_row, parse_document, search_passages, select_evidence


st.set_page_config(page_title="文献阅读助手", page_icon="📚", layout="wide")
st.title("📚 文献阅读助手")
st.caption("导入知网下载的论文、其他来源的文件，或通过 DOI 查找开放全文；回答附原文位置。")

if "documents" not in st.session_state:
    st.session_state.documents = {}
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None
if "last_matrix" not in st.session_state:
    st.session_state.last_matrix = None


def add_document(name: str, data: bytes, source: str) -> None:
    digest = hashlib.sha256(data).hexdigest()
    if any(info["digest"] == digest for info in st.session_state.documents.values()):
        return
    if len(st.session_state.documents) >= 8:
        st.warning("一次最多分析 8 篇文献，请先移除一些文件。")
        return
    passages, warnings = parse_document(name, data)
    if not passages:
        st.warning("该文件没有可读文字，可能需要先做 OCR。")
        return
    display = name
    counter = 2
    while display in st.session_state.documents:
        display = f"{name} ({counter})"
        counter += 1
    passages = [Passage(display, p.locator, p.text) for p in passages]
    st.session_state.documents[display] = {"digest": digest, "passages": passages, "warnings": warnings, "source": source}
    st.session_state.last_answer = None
    st.session_state.last_matrix = None
    st.success(f"已导入：{display}（{len(passages)} 个可检索片段）")


with st.sidebar:
    st.header("模型设置")
    api_key = st.text_input("模型 API 密钥", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    model = st.text_input("模型名称", value=os.getenv("LITERATURE_MODEL", "gpt-4o-mini"))
    api_base = st.text_input("兼容 OpenAI 的 API 地址", value=os.getenv("LITERATURE_API_BASE", "https://api.openai.com/v1"))
    st.caption("分析时选中的原文片段会发送给你填写的模型服务。请勿在公开部署中共享个人密钥。")
    st.caption("上传文献只保存在当前会话内；关闭会话后请重新导入。API 用量按所用服务计费。本机模型可留空密钥。")

tab_upload, tab_doi = st.tabs(["上传文献", "通过 DOI 导入开放论文"])
with tab_upload:
    files = st.file_uploader("选择 PDF、DOCX、TXT 或 MD（知网 CAJ 请先导出 PDF）", type=["pdf", "docx", "txt", "md"], accept_multiple_files=True)
    if files and st.button("导入所选文件", type="primary"):
        for file in files:
            try:
                add_document(file.name, file.getvalue(), "手动上传")
            except ValueError as exc:
                st.error(f"{file.name}：{exc}")

with tab_doi:
    doi = st.text_input("DOI 或 doi.org 链接", placeholder="10.1038/s41586-020-2649-2")
    openalex_key = st.text_input("OpenAlex API key（可选）", type="password")
    if st.button("查找并导入开放 PDF"):
        try:
            with st.spinner("正在查找开放版本…"):
                name, data, link = open_pdf_by_doi(doi, openalex_key)
                add_document(name, data, link)
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))

if st.session_state.documents:
    st.subheader("已导入文献")
    selected = st.multiselect("选择本次分析的文献", list(st.session_state.documents), default=list(st.session_state.documents))
    for name, info in st.session_state.documents.items():
        with st.expander(f"{name} · {len(info['passages'])} 个片段"):
            st.write("来源：", info["source"])
            for warning in info["warnings"][:8]:
                st.warning(warning)
            if len(info["warnings"]) > 8:
                st.caption(f"还有 {len(info['warnings']) - 8} 条提取提醒。")
            if st.button("移除此文献", key="remove_" + name):
                del st.session_state.documents[name]
                st.session_state.last_answer = None
                st.session_state.last_matrix = None
                st.rerun()

    question = st.text_area("你想了解什么？", placeholder="例如：对比这几篇论文的研究问题、理论框架、研究方法和主要结论，并指出研究空白。", height=90)
    st.caption("也可以问：这篇文章的研究方法有哪些局限？或：哪些文献讨论了基层政府与村民自治的关系？")
    if st.button("开始分析", type="primary", disabled=not selected):
        if not question.strip():
            st.warning("请先填写分析问题。")
        else:
            passages = [passage for name in selected for passage in st.session_state.documents[name]["passages"]]
            evidence = select_evidence(question, passages)
            try:
                with st.spinner("正在核对原文并生成分析…"):
                    result = analyze(question, evidence, api_key, model, api_base)
                st.session_state.last_answer = (question, result, evidence)
            except (ValueError, RuntimeError) as exc:
                st.error(str(exc))

    if st.session_state.last_answer:
        previous_question, result, evidence = st.session_state.last_answer
        lookup = dict(evidence)
        st.subheader("分析结果")
        st.caption("问题：" + previous_question)
        if not result["claims"]:
            st.warning("模型没有返回带有效证据编号的观点，请缩小提问范围再试。")
        lines = ["# 文献分析", "", f"问题：{previous_question}", ""]
        records = []
        for i, claim in enumerate(result["claims"], 1):
            references = [f"《{lookup[key].document}》{lookup[key].locator} [{key}]" for key in claim["sources"]]
            st.markdown(f"**{i}. {claim['text']}**")
            st.caption("来源：" + "；".join(references))
            lines.extend([f"{i}. {claim['text']}（{'；'.join(references)}）", ""])
            records.append({"观点": claim["text"], "文献与位置": "；".join(references)})
        if result["limits"]:
            st.info("检索范围与局限：" + result["limits"])
            lines.extend(["## 检索范围与局限", result["limits"], ""])
        with st.expander("核对原文片段"):
            used = {key for claim in result["claims"] for key in claim["sources"]}
            for key, passage in evidence:
                if key in used:
                    st.markdown(f"**[{key}] 《{passage.document}》{passage.locator}**")
                    st.text(passage.text)
                    lines.extend([f"### [{key}] 《{passage.document}》{passage.locator}", passage.text, ""])
        st.caption("页码指 PDF 文件中的页序，可能与期刊印刷页码不同；引用到正式论文前请人工核对原文与著录信息。")
        st.download_button("下载 Markdown 阅读笔记", "\n".join(lines).encode("utf-8"), file_name="文献阅读笔记.md", mime="text/markdown")
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=["观点", "文献与位置"])
        writer.writeheader()
        writer.writerows(records)
        st.download_button("下载观点索引 CSV", "\ufeff" + buffer.getvalue(), file_name="文献观点索引.csv", mime="text/csv")

    st.divider()
    st.subheader("全文定位")
    search_term = st.text_input("查找词句（无需模型密钥）", placeholder="例如：压力型体制")
    if len(search_term.strip()) >= 2:
        selected_passages = [p for name in selected for p in st.session_state.documents[name]["passages"]]
        matches = search_passages(search_term, selected_passages, limit=30)
        st.caption(f"显示前 {len(matches)} 处匹配；搜索范围是已提取的文字。")
        for p in matches:
            with st.expander(f"《{p.document}》{p.locator}"):
                st.text(p.text)

    st.divider()
    st.subheader("文献对照表")
    st.caption("按篇提取研究问题、理论框架、方法、样本、结论及局限；每篇调用一次模型，请核对表中原文位置。")
    if st.button("生成文献对照表", disabled=not selected):
        rows = []
        progress = st.progress(0)
        for index, name in enumerate(selected, 1):
            try:
                rows.append(paper_matrix_row(name, st.session_state.documents[name]["passages"], api_key, model, api_base))
            except (ValueError, RuntimeError) as exc:
                st.error(f"《{name}》分析失败：{exc}")
            progress.progress(index / len(selected))
        st.session_state.last_matrix = (tuple(selected), rows)
    saved_matrix = st.session_state.last_matrix
    if saved_matrix and saved_matrix[0] == tuple(selected) and saved_matrix[1]:
        rows = saved_matrix[1]
        st.dataframe([{key: row[key] for key in ("文献", *MATRIX_FIELDS)} for row in rows], hide_index=True, use_container_width=True)
        matrix_buffer = io.StringIO()
        columns = ["文献"] + [column for field in MATRIX_FIELDS for column in (field, field + "_出处")]
        writer = csv.DictWriter(matrix_buffer, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
        st.download_button("下载含出处的文献对照表 CSV", "\ufeff" + matrix_buffer.getvalue(), file_name="文献对照表.csv", mime="text/csv")
else:
    st.info("先导入一篇或多篇文献，即可开始提问。")
