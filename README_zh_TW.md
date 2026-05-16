<div align="center">

<img src="https://img.shields.io/badge/MarkdownMind-1.0.0-blue?style=for-the-badge" alt="版本">
<img src="https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python" alt="Python">
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="授權">

# 🧠 MarkdownMind

**輕量級Markdown文件智慧處理工具**

[English](README.md) | [简体中文](README_zh.md) | [繁體中文](README_zh_TW.md)

</div>

---

## 🎉 專案介紹

MarkdownMind 是一個輕量級、智慧化的 Markdown 文件處理工具，旨在幫助開發者和寫作者創建更優質的文件。它提供全面的文件分析、大綱生成、品質評分和差異比對功能。

### ✨ 為什麼選擇 MarkdownMind？

- 📊 **深度分析** - 超越簡單統計，分析文件結構和邏輯
- 🎯 **品質評分** - 多維度品質評估，提供可操作的改進建議
- 🗺️ **視覺化大綱** - 生成可互動的文件結構樹
- 🔄 **智慧比對** - 不僅是文字比對，還能檢測結構變化
- 🚀 **零依賴** - 核心功能無需外部依賴
- 💻 **CLI優先** - 命令列介面，輕鬆整合到工作流程

---

## ✨ 核心特性

### 📊 文件分析
- **結構分析** - 標題層級、章節關係
- **統計資訊** - 字數、段落數、程式碼區塊等
- **閱讀時間** - 基於內容估算閱讀時間
- **複雜度評分** - 文件複雜度評估

### ⭐ 品質評分
五個維度的品質評估：
- **可讀性** - 句子長度、詞彙複雜度
- **完整性** - 必要章節、中繼資料完整性
- **一致性** - 格式統一性、標題連續性
- **結構性** - 章節平衡、層級合理性
- **吸引力** - 圖片、連結、程式碼範例

### 🗺️ 大綱生成
多種輸出格式：
- Markdown 列表
- JSON 結構
- Mermaid 心智圖
- HTML 互動式大綱
- YAML 格式
- 純文字

### 🔄 文件比對
- 逐行比對
- 結構變更檢測
- 彩色終端輸出
- HTML 差異報告
- 統一差異格式

---

## 🚀 快速開始

### 安裝

```bash
# 使用 pip
pip install markdownmind

# 或從原始碼安裝
git clone https://github.com/gitstq/markdownmind.git
cd markdownmind
pip install -e .
```

### 環境要求

- Python 3.8 或更高版本
- click >= 8.0.0
- rich >= 13.0.0

### 基本用法

```bash
# 分析文件
markdownmind analyze document.md

# 生成大綱
markdownmind outline document.md --format mermaid

# 評分文件品質
markdownmind score document.md

# 比對兩個文件
markdownmind diff old.md new.md

# 取得統計資訊
markdownmind stats document.md
```

---

## 📖 詳細使用指南

### Analyze 指令

```bash
# 基礎分析
markdownmind analyze document.md

# 輸出到檔案
markdownmind analyze document.md -o report.html --format html

# JSON 輸出
markdownmind analyze document.md --format json
```

### Outline 指令

```bash
# Markdown 大綱
markdownmind outline document.md

# Mermaid 心智圖
markdownmind outline document.md --format mermaid

# HTML 大綱
markdownmind outline document.md --format html -o outline.html

# JSON 結構
markdownmind outline document.md --format json
```

### Score 指令

```bash
# 品質評分
markdownmind score document.md

# JSON 輸出
markdownmind score document.md --format json
```

### Diff 指令

```bash
# 摘要比對
markdownmind diff old.md new.md

# 統一差異格式
markdownmind diff old.md new.md --format unified

# 彩色輸出
markdownmind diff old.md new.md --format colored

# HTML 報告
markdownmind diff old.md new.md --format html -o diff.html
```

### 批次處理

```bash
# 分析多個檔案
markdownmind batch file1.md file2.md file3.md

# 帶輸出
markdownmind batch *.md -o batch_results.json
```

---

## 💡 設計理念

### 輕量快速
- 最小化依賴
- 快速解析和分析
- 適合 CI/CD 整合

### 開發者友善
- 清晰的 CLI 介面
- 多種輸出格式
- 可操作的改進建議

### 可擴展
- 模組化架構
- 易於添加新的分析器
- 外掛友善設計

---

## 📦 打包與部署

### 開發環境設定

```bash
# 克隆倉庫
git clone https://github.com/gitstq/markdownmind.git
cd markdownmind

# 安裝開發依賴
pip install -e ".[dev]"

# 執行測試
pytest

# 程式碼格式化
black markdownmind/
```

### 專案結構

```
markdownmind/
├── markdownmind/       # 主套件
│   ├── __init__.py
│   ├── parser.py       # Markdown 解析器
│   ├── analyzer.py     # 文件分析器
│   ├── scorer.py       # 品質評分器
│   ├── outline.py      # 大綱生成器
│   ├── diff.py         # 差異比對器
│   ├── formatter.py    # 輸出格式化器
│   └── cli.py          # CLI 介面
├── tests/              # 測試套件
├── docs/               # 文件
└── examples/           # 範例檔案
```

---

## 🤝 貢獻指南

歡迎貢獻！請隨時提交 Pull Request。

1. Fork 本倉庫
2. 建立您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

請確保：
- 遵循現有程式碼風格
- 為新功能添加測試
- 根據需要更新文件

---

## 📄 開源授權

本專案採用 MIT 授權開源 - 詳見 [LICENSE](LICENSE) 檔案。

---

## 🙏 致謝

- 靈感來源於對更好的文件工具的需求
- 用 Python 和愛心構建
- 感謝所有貢獻者

---

<div align="center">

**由 gitstq 用 ❤️ 製作**

如果這個專案對您有幫助，請 [⭐ Star 本倉庫](https://github.com/gitstq/markdownmind)！

</div>
