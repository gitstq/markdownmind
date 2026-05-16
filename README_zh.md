<div align="center">

<img src="https://img.shields.io/badge/MarkdownMind-1.0.0-blue?style=for-the-badge" alt="版本">
<img src="https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python" alt="Python">
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="许可证">

# 🧠 MarkdownMind

**轻量级Markdown文档智能处理工具**

[English](README.md) | [简体中文](README_zh.md) | [繁體中文](README_zh_TW.md)

</div>

---

## 🎉 项目介绍

MarkdownMind 是一个轻量级、智能化的 Markdown 文档处理工具，旨在帮助开发者和写作者创建更优质的文档。它提供全面的文档分析、大纲生成、质量评分和差异对比功能。

### ✨ 为什么选择 MarkdownMind？

- 📊 **深度分析** - 超越简单统计，分析文档结构和逻辑
- 🎯 **质量评分** - 多维度质量评估，提供可操作的改进建议
- 🗺️ **可视化大纲** - 生成可交互的文档结构树
- 🔄 **智能对比** - 不仅是文本对比，还能检测结构变化
- 🚀 **零依赖** - 核心功能无需外部依赖
- 💻 **CLI优先** - 命令行界面，轻松集成到工作流

---

## ✨ 核心特性

### 📊 文档分析
- **结构分析** - 标题层级、章节关系
- **统计信息** - 字数、段落数、代码块等
- **阅读时间** - 基于内容估算阅读时间
- **复杂度评分** - 文档复杂度评估

### ⭐ 质量评分
五个维度的质量评估：
- **可读性** - 句子长度、词汇复杂度
- **完整性** - 必要章节、元数据完整性
- **一致性** - 格式统一性、标题连续性
- **结构性** - 章节平衡、层级合理性
- **吸引力** - 图片、链接、代码示例

### 🗺️ 大纲生成
多种输出格式：
- Markdown 列表
- JSON 结构
- Mermaid 思维导图
- HTML 交互式大纲
- YAML 格式
- 纯文本

### 🔄 文档对比
- 逐行对比
- 结构变更检测
- 彩色终端输出
- HTML 差异报告
- 统一差异格式

---

## 🚀 快速开始

### 安装

```bash
# 使用 pip
pip install markdownmind

# 或从源码安装
git clone https://github.com/gitstq/markdownmind.git
cd markdownmind
pip install -e .
```

### 环境要求

- Python 3.8 或更高版本
- click >= 8.0.0
- rich >= 13.0.0

### 基本用法

```bash
# 分析文档
markdownmind analyze document.md

# 生成大纲
markdownmind outline document.md --format mermaid

# 评分文档质量
markdownmind score document.md

# 对比两个文档
markdownmind diff old.md new.md

# 获取统计信息
markdownmind stats document.md
```

---

## 📖 详细使用指南

### Analyze 命令

```bash
# 基础分析
markdownmind analyze document.md

# 输出到文件
markdownmind analyze document.md -o report.html --format html

# JSON 输出
markdownmind analyze document.md --format json
```

### Outline 命令

```bash
# Markdown 大纲
markdownmind outline document.md

# Mermaid 思维导图
markdownmind outline document.md --format mermaid

# HTML 大纲
markdownmind outline document.md --format html -o outline.html

# JSON 结构
markdownmind outline document.md --format json
```

### Score 命令

```bash
# 质量评分
markdownmind score document.md

# JSON 输出
markdownmind score document.md --format json
```

### Diff 命令

```bash
# 摘要对比
markdownmind diff old.md new.md

# 统一差异格式
markdownmind diff old.md new.md --format unified

# 彩色输出
markdownmind diff old.md new.md --format colored

# HTML 报告
markdownmind diff old.md new.md --format html -o diff.html
```

### 批量处理

```bash
# 分析多个文件
markdownmind batch file1.md file2.md file3.md

# 带输出
markdownmind batch *.md -o batch_results.json
```

---

## 💡 设计思路

### 轻量快速
- 最小化依赖
- 快速解析和分析
- 适合 CI/CD 集成

### 开发者友好
- 清晰的 CLI 界面
- 多种输出格式
- 可操作的改进建议

### 可扩展
- 模块化架构
- 易于添加新的分析器
- 插件友好设计

---

## 📦 打包与部署

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/gitstq/markdownmind.git
cd markdownmind

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black markdownmind/
```

### 项目结构

```
markdownmind/
├── markdownmind/       # 主包
│   ├── __init__.py
│   ├── parser.py       # Markdown 解析器
│   ├── analyzer.py     # 文档分析器
│   ├── scorer.py       # 质量评分器
│   ├── outline.py      # 大纲生成器
│   ├── diff.py         # 差异对比器
│   ├── formatter.py    # 输出格式化器
│   └── cli.py          # CLI 界面
├── tests/              # 测试套件
├── docs/               # 文档
└── examples/           # 示例文件
```

---

## 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

请确保：
- 遵循现有代码风格
- 为新功能添加测试
- 根据需要更新文档

---

## 📄 开源协议

本项目采用 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- 灵感来源于对更好的文档工具的需求
- 用 Python 和爱心构建
- 感谢所有贡献者

---

<div align="center">

**由 gitstq 用 ❤️ 制作**

如果这个项目对您有帮助，请 [⭐ Star 本仓库](https://github.com/gitstq/markdownmind)！

</div>
