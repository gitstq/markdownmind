"""
MarkdownMind - 轻量级Markdown文档智能处理工具

一个专注于文档结构分析、大纲生成、质量评估和可视化的Python工具库。
"""

__version__ = "1.0.0"
__author__ = "gitstq"
__license__ = "MIT"

from .parser import MarkdownParser
from .analyzer import DocumentAnalyzer
from .scorer import DocumentScorer
from .outline import OutlineGenerator
from .diff import DocumentDiff

__all__ = [
    "MarkdownParser",
    "DocumentAnalyzer",
    "DocumentScorer",
    "OutlineGenerator",
    "DocumentDiff",
]
