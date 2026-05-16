"""
Markdown文档解析模块

提供Markdown文档的解析、AST生成、元数据提取等功能。
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class NodeType(Enum):
    """文档节点类型"""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"
    LIST = "list"
    LIST_ITEM = "list_item"
    QUOTE = "quote"
    TABLE = "table"
    HORIZONTAL_RULE = "horizontal_rule"
    LINK = "link"
    IMAGE = "image"
    TEXT = "text"


@dataclass
class DocumentNode:
    """文档节点"""
    type: NodeType
    content: str = ""
    level: int = 0  # 用于标题层级
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List['DocumentNode'] = field(default_factory=list)
    line_number: int = 0


@dataclass
class DocumentMeta:
    """文档元数据"""
    title: str = ""
    author: str = ""
    date: str = ""
    tags: List[str] = field(default_factory=list)
    description: str = ""
    custom: Dict[str, str] = field(default_factory=dict)


@dataclass
class ParseResult:
    """解析结果"""
    nodes: List[DocumentNode] = field(default_factory=list)
    meta: DocumentMeta = field(default_factory=DocumentMeta)
    statistics: Dict[str, int] = field(default_factory=dict)
    raw_content: str = ""


class MarkdownParser:
    """Markdown解析器"""

    # YAML Front Matter 正则
    FRONT_MATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    
    # 标题正则
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$')
    
    # 代码块正则
    CODE_BLOCK_PATTERN = re.compile(r'^```(\w*)\s*\n(.*?)```$', re.DOTALL)
    
    # 行内代码正则
    INLINE_CODE_PATTERN = re.compile(r'`([^`]+)`')
    
    # 链接正则
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    # 图片正则
    IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    
    # 列表项正则
    LIST_ITEM_PATTERN = re.compile(r'^(\s*)[-*+]\s+(.+)$')
    ORDERED_LIST_PATTERN = re.compile(r'^(\s*)\d+\.\s+(.+)$')
    
    # 引用正则
    QUOTE_PATTERN = re.compile(r'^>\s*(.+)$')
    
    # 分隔线正则
    HR_PATTERN = re.compile(r'^(---|___|\*\*\*)\s*$')

    def __init__(self):
        self.reset()

    def reset(self):
        """重置解析器状态"""
        self.line_number = 0
        self.in_code_block = False
        self.code_buffer = []
        self.code_language = ""

    def parse(self, content: str) -> ParseResult:
        """
        解析Markdown内容
        
        Args:
            content: Markdown文本内容
            
        Returns:
            ParseResult: 解析结果
        """
        self.reset()
        result = ParseResult(raw_content=content)
        
        # 提取Front Matter
        content = self._extract_front_matter(content, result)
        
        # 按行解析
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            self.line_number = i + 1
            line = lines[i]
            
            # 处理代码块
            if line.startswith('```'):
                if not self.in_code_block:
                    self.in_code_block = True
                    self.code_language = line[3:].strip()
                    self.code_buffer = []
                else:
                    self.in_code_block = False
                    code_content = '\n'.join(self.code_buffer)
                    node = DocumentNode(
                        type=NodeType.CODE_BLOCK,
                        content=code_content,
                        metadata={"language": self.code_language},
                        line_number=self.line_number - len(self.code_buffer)
                    )
                    result.nodes.append(node)
                i += 1
                continue
            
            if self.in_code_block:
                self.code_buffer.append(line)
                i += 1
                continue
            
            # 解析普通行
            node = self._parse_line(line)
            if node:
                result.nodes.append(node)
            
            i += 1
        
        # 计算统计信息
        result.statistics = self._calculate_statistics(result.nodes)
        
        return result

    def parse_file(self, filepath: str) -> ParseResult:
        """
        从文件解析Markdown
        
        Args:
            filepath: 文件路径
            
        Returns:
            ParseResult: 解析结果
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parse(content)

    def _extract_front_matter(self, content: str, result: ParseResult) -> str:
        """提取YAML Front Matter"""
        match = self.FRONT_MATTER_PATTERN.match(content)
        if match:
            yaml_content = match.group(1)
            # 简单解析YAML格式
            for line in yaml_content.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    
                    if key == 'title':
                        result.meta.title = value
                    elif key == 'author':
                        result.meta.author = value
                    elif key == 'date':
                        result.meta.date = value
                    elif key == 'description':
                        result.meta.description = value
                    elif key == 'tags':
                        # 处理数组格式 [tag1, tag2] 或单行格式
                        value = value.strip('[]')
                        result.meta.tags = [t.strip().strip('"\'') for t in value.split(',') if t.strip()]
                    else:
                        result.meta.custom[key] = value
            
            return content[match.end():]
        return content

    def _parse_line(self, line: str) -> Optional[DocumentNode]:
        """解析单行内容"""
        stripped = line.strip()
        
        if not stripped:
            return None
        
        # 标题
        heading_match = self.HEADING_PATTERN.match(stripped)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2).strip()
            return DocumentNode(
                type=NodeType.HEADING,
                content=content,
                level=level,
                line_number=self.line_number
            )
        
        # 分隔线
        if self.HR_PATTERN.match(stripped):
            return DocumentNode(
                type=NodeType.HORIZONTAL_RULE,
                line_number=self.line_number
            )
        
        # 无序列表
        list_match = self.LIST_ITEM_PATTERN.match(line)
        if list_match:
            return DocumentNode(
                type=NodeType.LIST_ITEM,
                content=list_match.group(2),
                metadata={"indent": len(list_match.group(1))},
                line_number=self.line_number
            )
        
        # 有序列表
        ordered_match = self.ORDERED_LIST_PATTERN.match(line)
        if ordered_match:
            return DocumentNode(
                type=NodeType.LIST_ITEM,
                content=ordered_match.group(2),
                metadata={"indent": len(ordered_match.group(1)), "ordered": True},
                line_number=self.line_number
            )
        
        # 引用
        quote_match = self.QUOTE_PATTERN.match(line)
        if quote_match:
            return DocumentNode(
                type=NodeType.QUOTE,
                content=quote_match.group(1),
                line_number=self.line_number
            )
        
        # 普通段落
        return DocumentNode(
            type=NodeType.PARAGRAPH,
            content=stripped,
            line_number=self.line_number
        )

    def _calculate_statistics(self, nodes: List[DocumentNode]) -> Dict[str, int]:
        """计算文档统计信息"""
        stats = {
            "total_lines": self.line_number,
            "heading_count": 0,
            "paragraph_count": 0,
            "code_block_count": 0,
            "list_item_count": 0,
            "quote_count": 0,
            "link_count": 0,
            "image_count": 0,
            "word_count": 0,
            "char_count": 0,
        }
        
        for node in nodes:
            if node.type == NodeType.HEADING:
                stats["heading_count"] += 1
                stats["word_count"] += len(node.content.split())
                stats["char_count"] += len(node.content)
            elif node.type == NodeType.PARAGRAPH:
                stats["paragraph_count"] += 1
                stats["word_count"] += len(node.content.split())
                stats["char_count"] += len(node.content)
                # 统计链接和图片
                stats["link_count"] += len(self.LINK_PATTERN.findall(node.content))
                stats["image_count"] += len(self.IMAGE_PATTERN.findall(node.content))
            elif node.type == NodeType.CODE_BLOCK:
                stats["code_block_count"] += 1
                stats["char_count"] += len(node.content)
            elif node.type == NodeType.LIST_ITEM:
                stats["list_item_count"] += 1
                stats["word_count"] += len(node.content.split())
                stats["char_count"] += len(node.content)
            elif node.type == NodeType.QUOTE:
                stats["quote_count"] += 1
                stats["word_count"] += len(node.content.split())
                stats["char_count"] += len(node.content)
        
        return stats

    def extract_headings(self, result: ParseResult) -> List[Dict[str, Any]]:
        """提取所有标题"""
        headings = []
        for node in result.nodes:
            if node.type == NodeType.HEADING:
                headings.append({
                    "level": node.level,
                    "content": node.content,
                    "line_number": node.line_number
                })
        return headings

    def extract_links(self, result: ParseResult) -> List[Dict[str, str]]:
        """提取所有链接"""
        links = []
        for node in result.nodes:
            if node.type in (NodeType.PARAGRAPH, NodeType.QUOTE, NodeType.LIST_ITEM):
                for match in self.LINK_PATTERN.finditer(node.content):
                    links.append({
                        "text": match.group(1),
                        "url": match.group(2)
                    })
        return links

    def extract_images(self, result: ParseResult) -> List[Dict[str, str]]:
        """提取所有图片"""
        images = []
        for node in result.nodes:
            if node.type in (NodeType.PARAGRAPH, NodeType.LIST_ITEM):
                for match in self.IMAGE_PATTERN.finditer(node.content):
                    images.append({
                        "alt": match.group(1),
                        "url": match.group(2)
                    })
        return images
