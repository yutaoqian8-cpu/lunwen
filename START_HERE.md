# 从这里开始：创建 GitHub 文献阅读智能体

项目已整理成可直接上传的仓库目录。建议仓库名：`literature-reader-agent`，仓库简介：`带原文出处的中文学术文献阅读与对照分析工具`。

## 一、把文件放进 GitHub

1. 在电脑上解压交付的 ZIP。打开解压后的目录，应当直接看到 `app.py`、`core.py` 和 `requirements.txt`。
2. 在 GitHub 新建**私有仓库**，仓库名可用 `literature-reader-agent`。如果 GitHub 询问是否自动创建 README、.gitignore 或 License，保持空白即可；本包里已有 README 和 .gitignore。
3. 打开新仓库，选 **Add file → Upload files**。把解压目录**里面的文件和目录**拖入页面并提交。不要把 ZIP 当成一个文件直接上传；不要再套一层 `literature_reader` 文件夹。
4. 上传后在仓库首页核对：根目录有 `app.py`、`core.py`、`requirements.txt`；另外应有 `.streamlit/config.toml`、`.github/workflows/check.yml`、`tests/test_core.py`。

从手机操作时，GitHub 网页的文件夹上传可能不便；用电脑浏览器上传整个解压目录更稳妥。论文 PDF、知网 CAJ 文件、API 密钥和笔记都不要放入仓库。

## 二、让网页运行起来

GitHub 用于存放代码，不会直接运行 Python 网页。在 [Streamlit Community Cloud](https://share.streamlit.io/) 创建应用，选择刚创建的仓库，分支选 `main`，入口文件填 `app.py`。服务会从根目录读取 `requirements.txt` 安装依赖。

启动后：在页面左侧输入自己的模型 API 密钥，再上传论文 PDF；不填密钥也能用“全文定位”查找原文。ChatGPT Plus 订阅不能代替 API 密钥。不要把密钥写进 GitHub 文件。

## 三、如果想让 GitHub 上的 AI 继续开发

可以把下面这段作为任务描述，连同本项目仓库交给你的编程智能体：

> 请在这个 Streamlit 文献阅读项目上迭代，不要从零覆盖已有文件。先阅读 README.md、core.py、app.py 与 tests/test_core.py。保持知网论文由用户自行取得并上传，不实现绕过账号、批量抓取或付费下载。所有结论必须附可检查的原文片段及文件页序；模型找不到依据时要明确留空。优先实现：①扫描 PDF 的中文 OCR；②逐篇阅读卡片与用户可编辑的备注；③RIS/BibTeX 元数据导入；④多篇文献的研究主题归类。每项改动更新测试与 README，API 密钥不得提交到仓库。先展示改动和验证结果，再部署。

## 目录说明

| 文件或目录 | 用途 |
| --- | --- |
| `app.py` | 页面、上传、提问、对照表与下载 |
| `core.py` | 文本提取、检索、DOI 和模型调用 |
| `requirements.txt` | 云端自动安装的 Python 依赖 |
| `.streamlit/config.toml` | 上传大小设置 |
| `.gitignore` | 排除密钥、论文和临时文件 |
| `tests/test_core.py` | 核心功能测试 |
| `.github/workflows/check.yml` | GitHub 推送后的自动检查 |
| `README.md` | 完整使用说明与限制 |

本项目目前是经过本地验证的代码包，尚未替你在 GitHub 创建仓库，也没有线上应用网址。
