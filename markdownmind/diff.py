"""
文档差异对比模块

提供文档差异检测、结构调整识别、统计变化报告等功能。
"""

import difflib
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from .parser import MarkdownParser, ParseResult, NodeType


class ChangeType(Enum):
    """变更类型"""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"
    MOVED = "moved"


@dataclass
class ContentChange:
    """内容变更"""
    type: ChangeType
    old_content: str = ""
    new_content: str = ""
    old_line: int = 0
    new_line: int = 0
    section: str = ""


@dataclass
class StructureChange:
    """结构变更"""
    type: ChangeType
    element_type: str  # heading, section, etc.
    old_position: int = 0
    new_position: int = 0
    content: str = ""
    details: str = ""


@dataclass
class DiffResult:
    """差异对比结果"""
    content_changes: List[ContentChange] = field(default_factory=list)
    structure_changes: List[StructureChange] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""


class DocumentDiff:
    """文档差异对比器"""

    def __init__(self):
        self.parser = MarkdownParser()

    def compare(self, old_content: str, new_content: str) -> DiffResult:
        """
        对比两份文档内容
        
        Args:
            old_content: 旧文档内容
            new_content: 新文档内容
            
        Returns:
            DiffResult: 差异结果
        """
        result = DiffResult()
        
        # 解析两份文档
        old_parse = self.parser.parse(old_content)
        new_parse = self.parser.parse(new_content)
        
        # 对比内容
        result.content_changes = self._compare_content(old_content, new_content)
        
        # 对比结构
        result.structure_changes = self._compare_structure(old_parse, new_parse)
        
        # 生成统计
        result.statistics = self._generate_statistics(
            old_parse, new_parse, result
        )
        
        # 生成摘要
        result.summary = self._generate_summary(result)
        
        return result

    def compare_files(self, old_path: str, new_path: str) -> DiffResult:
        """
        对比两个文件
        
        Args:
            old_path: 旧文件路径
            new_path: 新文件路径
            
        Returns:
            DiffResult: 差异结果
        """
        with open(old_path, 'r', encoding='utf-8') as f:
            old_content = f.read()
        with open(new_path, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        return self.compare(old_content, new_content)

    def _compare_content(self, old_content: str, new_content: str) -> List[ContentChange]:
        """对比文本内容"""
        changes = []
        
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        # 使用difflib进行行级对比
        diff = list(difflib.unified_diff(
            old_lines, new_lines,
            lineterm='',
            n=3
        ))
        
        if not diff:
            return changes
        
        # 解析diff输出
        old_line_num = 0
        new_line_num = 0
        i = 2  # 跳过文件头
        
        while i < len(diff):
            line = diff[i]
            
            if line.startswith('@@'):
                # 解析行号信息
                match = re.match(r'@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
                if match:
                    old_line_num = int(match.group(1))
                    new_line_num = int(match.group(2))
                i += 1
                continue
            
            if line.startswith('-'):
                changes.append(ContentChange(
                    type=ChangeType.REMOVED,
                    old_content=line[1:],
                    old_line=old_line_num,
                    new_line=0
                ))
                old_line_num += 1
            elif line.startswith('+'):
                changes.append(ContentChange(
                    type=ChangeType.ADDED,
                    new_content=line[1:],
                    old_line=0,
                    new_line=new_line_num
                ))
                new_line_num += 1
            else:
                old_line_num += 1
                new_line_num += 1
            
            i += 1
        
        return changes

    def _compare_structure(self, old_parse: ParseResult, 
                           new_parse: ParseResult) -> List[StructureChange]:
        """对比文档结构"""
        changes = []
        
        # 提取标题
        old_headings = self._extract_headings(old_parse)
        new_headings = self._extract_headings(new_parse)
        
        # 对比标题变化
        old_titles = {h['content'] for h in old_headings}
        new_titles = {h['content'] for h in new_headings}
        
        # 新增的标题
        for h in new_headings:
            if h['content'] not in old_titles:
                changes.append(StructureChange(
                    type=ChangeType.ADDED,
                    element_type="heading",
                    new_position=h['line_number'],
                    content=h['content'],
                    details=f"新增H{h['level']}标题"
                ))
        
        # 删除的标题
        for h in old_headings:
            if h['content'] not in new_titles:
                changes.append(StructureChange(
                    type=ChangeType.REMOVED,
                    element_type="heading",
                    old_position=h['line_number'],
                    content=h['content'],
                    details=f"删除H{h['level']}标题"
                ))
        
        # 层级变化的标题
        for old_h in old_headings:
            for new_h in new_headings:
                if old_h['content'] == new_h['content'] and old_h['level'] != new_h['level']:
                    changes.append(StructureChange(
                        type=ChangeType.MODIFIED,
                        element_type="heading_level",
                        old_position=old_h['line_number'],
                        new_position=new_h['line_number'],
                        content=old_h['content'],
                        details=f"标题层级从H{old_h['level']}变为H{new_h['level']}"
                    ))
        
        # 对比代码块
        old_code = self._extract_code_blocks(old_parse)
        new_code = self._extract_code_blocks(new_parse)
        
        if len(new_code) > len(old_code):
            changes.append(StructureChange(
                type=ChangeType.ADDED,
                element_type="code_block",
                details=f"新增{len(new_code) - len(old_code)}个代码块"
            ))
        elif len(new_code) < len(old_code):
            changes.append(StructureChange(
                type=ChangeType.REMOVED,
                element_type="code_block",
                details=f"删除{len(old_code) - len(new_code)}个代码块"
            ))
        
        return changes

    def _extract_headings(self, parse_result: ParseResult) -> List[Dict[str, Any]]:
        """提取标题信息"""
        return self.parser.extract_headings(parse_result)

    def _extract_code_blocks(self, parse_result: ParseResult) -> List[Dict[str, Any]]:
        """提取代码块信息"""
        code_blocks = []
        for node in parse_result.nodes:
            if node.type == NodeType.CODE_BLOCK:
                code_blocks.append({
                    "language": node.metadata.get("language", ""),
                    "line_number": node.line_number
                })
        return code_blocks

    def _generate_statistics(self, old_parse: ParseResult, 
                            new_parse: ParseResult,
                            diff_result: DiffResult) -> Dict[str, Any]:
        """生成差异统计"""
        old_stats = old_parse.statistics
        new_stats = new_parse.statistics
        
        added_lines = sum(1 for c in diff_result.content_changes if c.type == ChangeType.ADDED)
        removed_lines = sum(1 for c in diff_result.content_changes if c.type == ChangeType.REMOVED)
        
        return {
            "old_document": {
                "word_count": old_stats.get("word_count", 0),
                "heading_count": old_stats.get("heading_count", 0),
                "paragraph_count": old_stats.get("paragraph_count", 0),
                "code_block_count": old_stats.get("code_block_count", 0),
            },
            "new_document": {
                "word_count": new_stats.get("word_count", 0),
                "heading_count": new_stats.get("heading_count", 0),
                "paragraph_count": new_stats.get("paragraph_count", 0),
                "code_block_count": new_stats.get("code_block_count", 0),
            },
            "changes": {
                "added_lines": added_lines,
                "removed_lines": removed_lines,
                "net_change": added_lines - removed_lines,
                "word_count_change": new_stats.get("word_count", 0) - old_stats.get("word_count", 0),
                "structure_changes": len(diff_result.structure_changes),
            }
        }

    def _generate_summary(self, diff_result: DiffResult) -> str:
        """生成差异摘要"""
        stats = diff_result.statistics
        changes = stats.get("changes", {})
        
        lines = ["### 变更摘要\n"]
        
        # 行数变化
        added = changes.get("added_lines", 0)
        removed = changes.get("removed_lines", 0)
        net = changes.get("net_change", 0)
        
        lines.append(f"📊 **行数变化**: +{added} / -{removed} (净变化: {net:+d})")
        
        # 字数变化
        word_change = changes.get("word_count_change", 0)
        if word_change != 0:
            lines.append(f"📝 **字数变化**: {word_change:+d} 字")
        
        # 结构变化
        structure_changes = changes.get("structure_changes", 0)
        if structure_changes > 0:
            lines.append(f"🏗️ **结构变更**: {structure_changes} 处")
        
        # 详细结构变化
        if diff_result.structure_changes:
            lines.append("\n#### 结构变更详情")
            for change in diff_result.structure_changes:
                emoji = {
                    ChangeType.ADDED: "➕",
                    ChangeType.REMOVED: "➖",
                    ChangeType.MODIFIED: "📝",
                    ChangeType.MOVED: "📦",
                }.get(change.type, "•")
                lines.append(f"{emoji} {change.details}: {change.content[:50]}..." if len(change.content) > 50 else f"{emoji} {change.details}: {change.content}")
        
        return "\n".join(lines)

    def generate_unified_diff(self, old_content: str, new_content: str,
                              old_name: str = "old", new_name: str = "new",
                              context_lines: int = 3) -> str:
        """
        生成统一格式的diff
        
        Args:
            old_content: 旧内容
            new_content: 新内容
            old_name: 旧文件名
            new_name: 新文件名
            context_lines: 上下文行数
            
        Returns:
            str: 统一格式的diff
        """
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        diff = difflib.unified_diff(
            old_lines, new_lines,
            fromfile=old_name,
            tofile=new_name,
            lineterm='',
            n=context_lines
        )
        
        return '\n'.join(diff)

    def generate_colored_diff(self, old_content: str, new_content: str) -> str:
        """
        生成带颜色标记的diff（用于终端显示）
        
        Args:
            old_content: 旧内容
            new_content: 新内容
            
        Returns:
            str: 带ANSI颜色代码的diff
        """
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        diff = list(difflib.unified_diff(
            old_lines, new_lines,
            lineterm='',
            n=3
        ))
        
        colored_lines = []
        for line in diff:
            if line.startswith('@@'):
                colored_lines.append(f"\033[36m{line}\033[0m")  # 青色
            elif line.startswith('-'):
                colored_lines.append(f"\033[31m{line}\033[0m")  # 红色
            elif line.startswith('+'):
                colored_lines.append(f"\033[32m{line}\033[0m")  # 绿色
            else:
                colored_lines.append(line)
        
        return '\n'.join(colored_lines)

    def generate_html_diff(self, old_content: str, new_content: str) -> str:
        """
        生成HTML格式的diff
        
        Args:
            old_content: 旧内容
            new_content: 新内容
            
        Returns:
            str: HTML格式的diff
        """
        diff = difflib.HtmlDiff(wrapcolumn=80)
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        return diff.make_file(
            old_lines, new_lines,
            fromdesc="旧版本",
            todesc="新版本",
            context=True,
            numlines=3
        )
