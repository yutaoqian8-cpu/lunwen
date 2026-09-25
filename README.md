# 文献阅读助手

首次上传 GitHub 请先阅读 [START_HERE.md](START_HERE.md)。

面向公共管理及社会科学研究的个人阅读工具。支持知网或其他数据库下载的 PDF、DOCX、TXT、MD，以及 DOI 对应的开放 PDF。一次最多处理 8 篇：问答与比较、全文定位、生成附原文位置的文献对照表。

## 安装与运行

需要 Python 3.10 或更新版本。进入有 `app.py` 的项目目录，运行：

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows 无需激活虚拟环境，也可以在项目目录的命令提示符中依次运行 `py -m pip install -r requirements.txt` 和 `py -m streamlit run app.py`。

在浏览器页面左侧填写模型 API 密钥。默认是 OpenAI API 地址 `https://api.openai.com/v1` 和 `gpt-4o-mini`；也可以填写支持 OpenAI Chat Completions 和 JSON 模式的服务。使用本机兼容接口（例如本机部署的模型）时密钥可以留空，但模型仍须支持 JSON 模式。ChatGPT 订阅不包括 API 用量。

1. 从知网或学校图书馆按你的权限下载论文 PDF，上传至工具；知网 CAJ 文件先用有权限的阅读器导出 PDF。
2. 或输入 DOI，尝试导入开放版本；找不到开放 PDF 时，按第一种方式手动上传。
3. 选择本次要分析的文献，输入问题，例如“比较各篇关于行政化与村民自治的理论框架、研究方法和不足”。
4. 在“全文定位”中直接查找关键词，无需模型密钥。点击“生成文献对照表”，可以按篇整理研究问题、理论框架、方法、样本、结论和局限，每篇会产生一次模型调用。
5. 打开“核对原文片段”检查模型引用的位置；下载 Markdown 阅读笔记、CSV 观点索引或文献对照表。

## 部署到 GitHub + Streamlit Community Cloud

GitHub 保存**代码**，应用网页由 Streamlit Community Cloud 提供。

1. 新建一个**私有** GitHub 仓库，上传本项目中的 `app.py`、`core.py`、`requirements.txt`、`.streamlit/config.toml`、`.gitignore`、`tests/`、`.github/` 与本说明。不要上传论文、密钥、笔记或 `.streamlit/secrets.toml`。
2. 在 [share.streamlit.io](https://share.streamlit.io/) 用 GitHub 登录，创建应用并选择该仓库，主文件选择 `app.py`，分支选 `main`。
3. 部署成功后通过该应用的私有访问地址使用。部署在私有仓库上的应用默认只向获准访问的人开放，仍应按文献授权与隐私要求使用。
4. 若要使用私有 API 密钥，可在页面里自己输入。**不要**在公开仓库中填写密钥；共享应用时更不要配置一个所有访问者都能无限使用的密钥。

仓库推送和拉取请求会运行 `.github/workflows/check.yml` 中的测试。项目根目录可手动执行 `python -m unittest discover -s tests -v`。

## 能力范围

- 一次最多保留 8 篇文献，单文件上限 30 MB；PDF 最多解析前 250 页。
- PDF 页码是**文件中的页序**，不是论文的印刷页码。Word 文档以段落定位。
- 工具只抽取部分相关页段送入模型。跨全文的系统综述或准确的全文覆盖统计仍需要逐篇核查；篇幅很长的论文可按章节分次提问。
- 图片扫描 PDF 没有 OCR，会提示文字不足；公式、表格、双栏排版可能提取不完整。
- DOI 导入只尝试开放获取地址，不绕过知网或出版社登录。开放全文可能有独立版权，下载和使用应遵守来源授权。
- 页面会话中的上传文献暂存于运行进程；服务器维护方在技术上可接触运行环境。提问时会将选中的文本片段发给你配置的模型服务，生成对照表时每篇分别发送。未发表或敏感论文请先确认学校及所用模型服务的数据要求。
- 引用编号由程序校验是否属于本次检索片段；**观点是否真的受到片段支持仍需人工核对**。不要直接复制生成的引用为正式参考文献。

## 文件说明

- `app.py`：交互页面、文件管理和导出。
- `core.py`：按页提取、中文与英文检索、DOI 开放全文查找、调用模型。
- `requirements.txt`：依赖；`.gitignore`：避免意外提交论文与密钥。
- `tests/` 与 `.github/workflows/`：关键行为的自动检查。

本程序不提供知网账号接入、批量抓取、自动下载付费文章，也不代替图书馆授权。后续可加入 OCR、Zotero 导入和长期保存的研究主题文件夹。
