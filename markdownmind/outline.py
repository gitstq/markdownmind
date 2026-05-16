"""
文档大纲生成模块

提供文档大纲生成、思维导图导出、结构化输出等功能。
"""

import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from enum import Enum

from .parser import ParseResult
from .analyzer import AnalysisResult, Section


class OutlineFormat(Enum):
    """大纲输出格式"""
    JSON = "json"
    MARKDOWN = "markdown"
    MERMAID = "mermaid"
    HTML = "html"
    TEXT = "text"
    YAML = "yaml"


@dataclass
class OutlineNode:
    """大纲节点"""
    title: str
    level: int
    word_count: int = 0
    paragraph_count: int = 0
    line_start: int = 0
    line_end: int = 0
    children: List['OutlineNode'] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "title": self.title,
            "level": self.level,
            "word_count": self.word_count,
            "paragraph_count": self.paragraph_count,
            "line_range": f"{self.line_start}-{self.line_end}",
            "children": [c.to_dict() for c in self.children]
        }


class OutlineGenerator:
    """大纲生成器"""

    def __init__(self):
        pass

    def generate(self, analysis_result: AnalysisResult, 
                 format_type: OutlineFormat = OutlineFormat.MARKDOWN) -> str:
        """
        生成大纲
        
        Args:
            analysis_result: 分析结果
            format_type: 输出格式
            
        Returns:
            str: 格式化的大纲内容
        """
        # 构建大纲节点树
        outline_nodes = self._build_outline_nodes(analysis_result.sections)
        
        # 根据格式输出
        if format_type == OutlineFormat.JSON:
            return self._to_json(outline_nodes)
        elif format_type == OutlineFormat.MARKDOWN:
            return self._to_markdown(outline_nodes)
        elif format_type == OutlineFormat.MERMAID:
            return self._to_mermaid(outline_nodes)
        elif format_type == OutlineFormat.HTML:
            return self._to_html(outline_nodes)
        elif format_type == OutlineFormat.TEXT:
            return self._to_text(outline_nodes)
        elif format_type == OutlineFormat.YAML:
            return self._to_yaml(outline_nodes)
        else:
            return self._to_markdown(outline_nodes)

    def _build_outline_nodes(self, sections: List[Section]) -> List[OutlineNode]:
        """从章节构建大纲节点"""
        nodes = []
        for section in sections:
            node = OutlineNode(
                title=section.title,
                level=section.level,
                word_count=section.word_count,
                paragraph_count=section.paragraph_count,
                line_start=section.start_line,
                line_end=section.end_line,
                children=self._build_outline_nodes(section.subsections)
            )
            nodes.append(node)
        return nodes

    def _to_json(self, nodes: List[OutlineNode]) -> str:
        """生成JSON格式"""
        data = {
            "outline": [n.to_dict() for n in nodes],
            "total_sections": self._count_nodes(nodes),
            "max_depth": self._calculate_depth(nodes)
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    def _to_markdown(self, nodes: List[OutlineNode], 
                     include_stats: bool = True) -> str:
        """生成Markdown格式大纲"""
        lines = ["# 文档大纲\n"]
        
        def add_node(node: OutlineNode, prefix: str = ""):
            indent = "  " * (node.level - 1) if node.level > 0 else ""
            if include_stats and (node.word_count > 0 or node.paragraph_count > 0):
                stats = f" ({node.word_count}字, {node.paragraph_count}段)"
            else:
                stats = ""
            
            lines.append(f"{indent}- {node.title}{stats}")
            
            for child in node.children:
                add_node(child, prefix)
        
        for node in nodes:
            add_node(node)
        
        return "\n".join(lines)

    def _to_mermaid(self, nodes: List[OutlineNode]) -> str:
        """生成Mermaid思维导图格式"""
        lines = ["```mermaid", "mindmap", "  root((文档结构))"]
        
        def add_node(node: OutlineNode, indent_level: int = 2):
            indent = "  " * indent_level
            # 转义特殊字符
            title = node.title.replace('"', '\\"').replace('(', '\\(').replace(')', '\\)')
            
            if node.children:
                lines.append(f"{indent}({title})")
                for child in node.children:
                    add_node(child, indent_level + 1)
            else:
                lines.append(f"{indent}[{title}]")
        
        for node in nodes:
            add_node(node, 2)
        
        lines.append("```")
        return "\n".join(lines)

    def _to_html(self, nodes: List[OutlineNode]) -> str:
        """生成HTML格式大纲"""
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            '  <meta charset="UTF-8">',
            "  <title>文档大纲</title>",
            "  <style>",
            "    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }",
            "    h1 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }",
            "    .outline { list-style: none; padding: 0; }",
            "    .outline li { margin: 8px 0; padding: 8px 12px; border-radius: 4px; transition: background 0.2s; }",
            "    .outline li:hover { background: #f5f5f5; }",
            "    .level-1 { font-size: 1.2em; font-weight: bold; color: #2196F3; }",
            "    .level-2 { padding-left: 20px; font-weight: 600; color: #4CAF50; }",
            "    .level-3 { padding-left: 40px; color: #FF9800; }",
            "    .level-4 { padding-left: 60px; color: #9C27B0; }",
            "    .stats { font-size: 0.85em; color: #666; margin-left: 8px; }",
            "  </style>",
            "</head>",
            "<body>",
            "  <h1>📄 文档大纲</h1>",
            '  <ul class="outline">'
        ]
        
        def add_node(node: OutlineNode):
            level_class = f"level-{min(node.level, 4)}"
            stats = f'<span class="stats">({node.word_count}字)</span>' if node.word_count > 0 else ""
            html.append(f'    <li class="{level_class}">{node.title}{stats}</li>')
            for child in node.children:
                add_node(child)
        
        for node in nodes:
            add_node(node)
        
        html.extend([
            "  </ul>",
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html)

    def _to_text(self, nodes: List[OutlineNode]) -> str:
        """生成纯文本格式大纲"""
        lines = ["文档大纲", "=" * 40, ""]
        
        def add_node(node: OutlineNode, number_prefix: str = ""):
            indent = "    " * (node.level - 1) if node.level > 0 else ""
            current_number = f"{number_prefix}1." if not number_prefix else f"{number_prefix}1."
            
            # 计算实际序号
            if node.level == 0:
                current_number = ""
            
            lines.append(f"{indent}{current_number} {node.title}")
            
            for i, child in enumerate(node.children):
                child_prefix = f"{number_prefix}{i + 1}." if number_prefix else f"{i + 1}."
                add_node(child, child_prefix)
        
        for i, node in enumerate(nodes):
            add_node(node, f"{i + 1}.")
        
        return "\n".join(lines)

    def _to_yaml(self, nodes: List[OutlineNode]) -> str:
        """生成YAML格式大纲"""
        lines = ["outline:"]
        
        def add_node(node: OutlineNode, indent: int = 2):
            prefix = " " * indent
            lines.append(f'{prefix}- title: "{node.title}"')
            lines.append(f"{prefix}  level: {node.level}")
            lines.append(f"{prefix}  word_count: {node.word_count}")
            lines.append(f"{prefix}  paragraph_count: {node.paragraph_count}")
            lines.append(f"{prefix}  line_range: \"{node.line_start}-{node.line_end}\"")
            if node.children:
                lines.append(f"{prefix}  children:")
                for child in node.children:
                    add_node(child, indent + 4)
        
        for node in nodes:
            add_node(node, 2)
        
        return "\n".join(lines)

    def _count_nodes(self, nodes: List[OutlineNode]) -> int:
        """统计节点总数"""
        count = len(nodes)
        for node in nodes:
            count += self._count_nodes(node.children)
        return count

    def _calculate_depth(self, nodes: List[OutlineNode], current_depth: int = 1) -> int:
        """计算大纲深度"""
        if not nodes:
            return current_depth - 1
        
        max_depth = current_depth
        for node in nodes:
            if node.children:
                child_depth = self._calculate_depth(node.children, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth

    def generate_toc(self, parse_result: ParseResult, 
                     max_level: int = 3,
                     include_links: bool = False) -> str:
        """
        生成目录(TOC)
        
        Args:
            parse_result: 解析结果
            max_level: 最大标题层级
            include_links: 是否包含锚点链接
            
        Returns:
            str: Markdown格式的目录
        """
        headings = []
        for node in parse_result.nodes:
            if node.type == NodeType.HEADING and node.level <= max_level:
                headings.append(node)
        
        if not headings:
            return ""
        
        lines = ["## 目录\n"]
        
        for heading in headings:
            indent = "  " * (heading.level - 1)
            title = heading.content
            
            if include_links:
                # 生成锚点链接
                anchor = self._generate_anchor(title)
                lines.append(f"{indent}- [{title}](#{anchor})")
            else:
                lines.append(f"{indent}- {title}")
        
        lines.append("")
        return "\n".join(lines)

    def _generate_anchor(self, title: str) -> str:
        """生成锚点ID"""
        # 移除特殊字符，转换为小写
        anchor = title.lower()
        anchor = ''.join(c if c.isalnum() or c.isspace() else '-' for c in anchor)
        anchor = '-'.join(anchor.split())
        return anchor

    def generate_summary(self, parse_result: ParseResult, 
                        analysis_result: AnalysisResult) -> str:
        """
        生成文档摘要
        
        Args:
            parse_result: 解析结果
            analysis_result: 分析结果
            
        Returns:
            str: 文档摘要
        """
        stats = parse_result.statistics
        meta = parse_result.meta
        
        lines = ["## 文档摘要\n"]
        
        # 基本信息
        if meta.title:
            lines.append(f"**标题**: {meta.title}")
        if meta.author:
            lines.append(f"**作者**: {meta.author}")
        if meta.date:
            lines.append(f"**日期**: {meta.date}")
        if meta.description:
            lines.append(f"**描述**: {meta.description}")
        
        lines.append("")
        
        # 统计信息
        lines.append("### 统计信息")
        lines.append(f"- 总字数: {stats.get('word_count', 0)}")
        lines.append(f"- 段落数: {stats.get('paragraph_count', 0)}")
        lines.append(f"- 标题数: {stats.get('heading_count', 0)}")
        lines.append(f"- 代码块: {stats.get('code_block_count', 0)}")
        lines.append(f"- 预计阅读时间: {analysis_result.reading_time_minutes}分钟")
        lines.append("")
        
        # 结构信息
        lines.append("### 结构信息")
        lines.append(f"- 文档深度: {analysis_result.structure_depth}层")
        lines.append(f"- 结构平衡性: {analysis_result.structure_balance_score}%")
        lines.append("")
        
        return "\n".join(lines)
