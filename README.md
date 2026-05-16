<div align="center">

<img src="https://img.shields.io/badge/MarkdownMind-1.0.0-blue?style=for-the-badge" alt="Version">
<img src="https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python" alt="Python">
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">

# 🧠 MarkdownMind

**轻量级Markdown文档智能处理工具**

[English](README.md) | [简体中文](README_zh.md) | [繁體中文](README_zh_TW.md)

</div>

---

## 🎉 Introduction

MarkdownMind is a lightweight, intelligent Markdown document processing tool designed to help developers and writers create better documentation. It provides comprehensive document analysis, outline generation, quality scoring, and diff comparison features.

### ✨ Why MarkdownMind?

- 📊 **Deep Analysis** - Beyond simple statistics, analyzes document structure and logic
- 🎯 **Quality Scoring** - Multi-dimensional quality assessment with actionable suggestions
- 🗺️ **Visual Outlines** - Generate interactive document structure trees
- 🔄 **Smart Diff** - Not just text comparison, but structural change detection
- 🚀 **Zero Dependencies** - Core functionality requires no external dependencies
- 💻 **CLI First** - Command-line interface for easy integration into workflows

---

## ✨ Core Features

### 📊 Document Analysis
- **Structure Analysis** - Heading hierarchy, section relationships
- **Statistics** - Word count, paragraph count, code blocks, etc.
- **Reading Time** - Estimated reading time based on content
- **Complexity Score** - Document complexity assessment

### ⭐ Quality Scoring
Five dimensions of quality evaluation:
- **Readability** - Sentence length, vocabulary complexity
- **Completeness** - Required sections, metadata presence
- **Consistency** - Format uniformity, heading continuity
- **Structure** - Section balance, hierarchy合理性
- **Engagement** - Images, links, code examples

### 🗺️ Outline Generation
Multiple output formats:
- Markdown list
- JSON structure
- Mermaid mindmap
- HTML interactive outline
- YAML format
- Plain text

### 🔄 Document Diff
- Line-by-line comparison
- Structural change detection
- Colored terminal output
- HTML diff report
- Unified diff format

---

## 🚀 Quick Start

### Installation

```bash
# Using pip
pip install markdownmind

# Or install from source
git clone https://github.com/gitstq/markdownmind.git
cd markdownmind
pip install -e .
```

### Requirements

- Python 3.8 or higher
- click >= 8.0.0
- rich >= 13.0.0

### Basic Usage

```bash
# Analyze a document
markdownmind analyze document.md

# Generate outline
markdownmind outline document.md --format mermaid

# Score document quality
markdownmind score document.md

# Compare two documents
markdownmind diff old.md new.md

# Get statistics
markdownmind stats document.md
```

---

## 📖 Detailed Usage

### Analyze Command

```bash
# Basic analysis
markdownmind analyze document.md

# Output to file
markdownmind analyze document.md -o report.html --format html

# JSON output
markdownmind analyze document.md --format json
```

### Outline Command

```bash
# Markdown outline
markdownmind outline document.md

# Mermaid mindmap
markdownmind outline document.md --format mermaid

# HTML outline
markdownmind outline document.md --format html -o outline.html

# JSON structure
markdownmind outline document.md --format json
```

### Score Command

```bash
# Quality scoring
markdownmind score document.md

# JSON output
markdownmind score document.md --format json
```

### Diff Command

```bash
# Summary comparison
markdownmind diff old.md new.md

# Unified diff
markdownmind diff old.md new.md --format unified

# Colored output
markdownmind diff old.md new.md --format colored

# HTML report
markdownmind diff old.md new.md --format html -o diff.html
```

### Batch Processing

```bash
# Analyze multiple files
markdownmind batch file1.md file2.md file3.md

# With output
markdownmind batch *.md -o batch_results.json
```

---

## 💡 Design Philosophy

### Lightweight & Fast
- Minimal dependencies
- Fast parsing and analysis
- Suitable for CI/CD integration

### Developer-Friendly
- Clear CLI interface
- Multiple output formats
- Actionable suggestions

### Extensible
- Modular architecture
- Easy to add new analyzers
- Plugin-friendly design

---

## 📦 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/gitstq/markdownmind.git
cd markdownmind

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black markdownmind/
```

### Project Structure

```
markdownmind/
├── markdownmind/       # Main package
│   ├── __init__.py
│   ├── parser.py       # Markdown parser
│   ├── analyzer.py     # Document analyzer
│   ├── scorer.py       # Quality scorer
│   ├── outline.py      # Outline generator
│   ├── diff.py         # Diff comparator
│   ├── formatter.py    # Output formatter
│   └── cli.py          # CLI interface
├── tests/              # Test suite
├── docs/               # Documentation
└── examples/           # Example files
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please make sure to:
- Follow the existing code style
- Add tests for new features
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by the need for better documentation tools
- Built with Python and love
- Thanks to all contributors

---

<div align="center">

**Made with ❤️ by gitstq**

[⭐ Star this repo](https://github.com/gitstq/markdownmind) if you find it helpful!

</div>
