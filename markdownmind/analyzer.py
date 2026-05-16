"""
文档结构分析模块

提供文档结构分析、章节关联性计算、阅读时间估算等功能。
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from .parser import ParseResult, DocumentNode, NodeType


@dataclass
class Section:
    """文档章节"""
    title: str = ""
    level: int = 0
    start_line: int = 0
    end_line: int = 0
    content_nodes: List[DocumentNode] = field(default_factory=list)
    subsections: List['Section'] = field(default_factory=list)
    word_count: int = 0
    paragraph_count: int = 0
    code_block_count: int = 0


@dataclass
class AnalysisResult:
    """分析结果"""
    sections: List[Section] = field(default_factory=list)
    structure_depth: int = 0
    avg_section_length: float = 0.0
    structure_balance_score: float = 0.0
    reading_time_minutes: int = 0
    complexity_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)


class DocumentAnalyzer:
    """文档分析器"""

    # 平均阅读速度 (词/分钟)
    READING_SPEED = 200
    # 技术文档阅读速度 (词/分钟)
    TECH_READING_SPEED = 150

    def __init__(self, reading_speed: int = None):
        self.reading_speed = reading_speed or self.READING_SPEED

    def analyze(self, parse_result: ParseResult) -> AnalysisResult:
        """
        分析文档结构
        
        Args:
            parse_result: 解析结果
            
        Returns:
            AnalysisResult: 分析结果
        """
        result = AnalysisResult()
        
        # 构建章节结构
        result.sections = self._build_section_tree(parse_result.nodes)
        
        # 计算结构深度
        result.structure_depth = self._calculate_depth(result.sections)
        
        # 计算平均章节长度
        result.avg_section_length = self._calculate_avg_section_length(result.sections)
        
        # 计算结构平衡性
        result.structure_balance_score = self._calculate_balance_score(result.sections)
        
        # 估算阅读时间
        total_words = parse_result.statistics.get("word_count", 0)
        result.reading_time_minutes = math.ceil(total_words / self.reading_speed)
        
        # 计算复杂度
        result.complexity_score = self._calculate_complexity(parse_result, result)
        
        # 生成建议
        result.recommendations = self._generate_recommendations(parse_result, result)
        
        # 汇总统计
        result.statistics = self._compile_statistics(parse_result, result)
        
        return result

    def _build_section_tree(self, nodes: List[DocumentNode]) -> List[Section]:
        """构建章节树结构"""
        sections = []
        section_stack = []
        current_section = None
        current_content = []
        
        for node in nodes:
            if node.type == NodeType.HEADING:
                # 保存当前章节
                if current_section is not None:
                    current_section.content_nodes = current_content
                    current_section.end_line = node.line_number - 1
                    self._update_section_stats(current_section)
                    current_content = []
                
                # 创建新章节
                new_section = Section(
                    title=node.content,
                    level=node.level,
                    start_line=node.line_number
                )
                
                # 确定章节层级关系
                while section_stack and section_stack[-1].level >= node.level:
                    section_stack.pop()
                
                if section_stack:
                    section_stack[-1].subsections.append(new_section)
                else:
                    sections.append(new_section)
                
                section_stack.append(new_section)
                current_section = new_section
            else:
                if current_section is None:
                    # 创建默认章节（无标题内容）
                    current_section = Section(
                        title="(无标题)",
                        level=0,
                        start_line=node.line_number
                    )
                    sections.append(current_section)
                current_content.append(node)
        
        # 处理最后一个章节
        if current_section is not None and current_section.end_line == 0:
            current_section.content_nodes = current_content
            current_section.end_line = nodes[-1].line_number if nodes else current_section.start_line
            self._update_section_stats(current_section)
        
        return sections

    def _update_section_stats(self, section: Section):
        """更新章节统计信息"""
        word_count = 0
        paragraph_count = 0
        code_block_count = 0
        
        for node in section.content_nodes:
            if node.type == NodeType.PARAGRAPH:
                word_count += len(node.content.split())
                paragraph_count += 1
            elif node.type == NodeType.LIST_ITEM:
                word_count += len(node.content.split())
            elif node.type == NodeType.QUOTE:
                word_count += len(node.content.split())
            elif node.type == NodeType.CODE_BLOCK:
                code_block_count += 1
                word_count += len(node.content.split())
        
        section.word_count = word_count
        section.paragraph_count = paragraph_count
        section.code_block_count = code_block_count

    def _calculate_depth(self, sections: List[Section], current_depth: int = 1) -> int:
        """计算文档结构深度"""
        if not sections:
            return current_depth - 1
        
        max_depth = current_depth
        for section in sections:
            if section.subsections:
                sub_depth = self._calculate_depth(section.subsections, current_depth + 1)
                max_depth = max(max_depth, sub_depth)
        
        return max_depth

    def _calculate_avg_section_length(self, sections: List[Section]) -> float:
        """计算平均章节长度（字数）"""
        total_words = 0
        section_count = 0
        
        def count_sections(secs):
            nonlocal total_words, section_count
            for sec in secs:
                total_words += sec.word_count
                section_count += 1
                count_sections(sec.subsections)
        
        count_sections(sections)
        
        return total_words / section_count if section_count > 0 else 0

    def _calculate_balance_score(self, sections: List[Section]) -> float:
        """
        计算结构平衡性评分 (0-100)
        评估各章节长度的均匀程度
        """
        if not sections:
            return 100.0
        
        # 收集所有章节的字数
        word_counts = []
        
        def collect_counts(secs):
            for sec in secs:
                word_counts.append(sec.word_count)
                collect_counts(sec.subsections)
        
        collect_counts(sections)
        
        if len(word_counts) < 2:
            return 100.0
        
        # 计算变异系数 (CV)
        mean = sum(word_counts) / len(word_counts)
        if mean == 0:
            return 100.0
        
        variance = sum((x - mean) ** 2 for x in word_counts) / len(word_counts)
        std_dev = math.sqrt(variance)
        cv = (std_dev / mean) * 100
        
        # CV越低越平衡，转换为0-100分
        balance_score = max(0, 100 - cv)
        return round(balance_score, 2)

    def _calculate_complexity(self, parse_result: ParseResult, analysis_result: AnalysisResult) -> float:
        """
        计算文档复杂度评分 (0-100)
        基于结构深度、平均章节长度、代码块比例等因素
        """
        stats = parse_result.statistics
        
        # 结构复杂度 (基于深度)
        depth_score = min(analysis_result.structure_depth * 15, 40)
        
        # 内容复杂度 (基于字数)
        word_count = stats.get("word_count", 0)
        length_score = min(word_count / 100, 30)
        
        # 代码复杂度
        code_blocks = stats.get("code_block_count", 0)
        total_blocks = stats.get("paragraph_count", 1) + code_blocks
        code_ratio = code_blocks / total_blocks if total_blocks > 0 else 0
        code_score = code_ratio * 20
        
        # 链接/图片复杂度
        links = stats.get("link_count", 0)
        images = stats.get("image_count", 0)
        media_score = min((links + images) * 2, 10)
        
        total_score = depth_score + length_score + code_score + media_score
        return round(min(total_score, 100), 2)

    def _generate_recommendations(self, parse_result: ParseResult, analysis_result: AnalysisResult) -> List[str]:
        """生成改进建议"""
        recommendations = []
        stats = parse_result.statistics
        
        # 检查标题层级
        if analysis_result.structure_depth > 4:
            recommendations.append("📉 文档层级过深(>4层)，建议简化结构，提高可读性")
        elif analysis_result.structure_depth < 2 and stats.get("word_count", 0) > 500:
            recommendations.append("📚 文档内容较长但层级较少，建议增加子章节划分")
        
        # 检查平衡性
        if analysis_result.structure_balance_score < 50:
            recommendations.append("⚖️ 各章节长度差异较大，建议平衡内容分布")
        
        # 检查代码块
        if stats.get("code_block_count", 0) > 0:
            code_ratio = stats["code_block_count"] / max(stats.get("paragraph_count", 1), 1)
            if code_ratio > 0.5:
                recommendations.append("💻 代码占比较高，建议增加更多解释性文字")
        
        # 检查链接
        if stats.get("link_count", 0) == 0 and stats.get("word_count", 0) > 300:
            recommendations.append("🔗 文档中没有外部链接，建议添加相关参考资料")
        
        # 检查图片
        if stats.get("image_count", 0) == 0 and stats.get("word_count", 0) > 1000:
            recommendations.append("🖼️ 长文档缺少配图，建议添加图表提升可读性")
        
        # 阅读时间
        if analysis_result.reading_time_minutes > 20:
            recommendations.append("⏱️ 阅读时间超过20分钟，建议拆分为多篇文档")
        
        return recommendations

    def _compile_statistics(self, parse_result: ParseResult, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """汇总统计信息"""
        return {
            "basic": parse_result.statistics,
            "structure": {
                "depth": analysis_result.structure_depth,
                "section_count": self._count_all_sections(analysis_result.sections),
                "balance_score": analysis_result.structure_balance_score,
            },
            "reading": {
                "time_minutes": analysis_result.reading_time_minutes,
                "time_formatted": f"{analysis_result.reading_time_minutes // 60}h {analysis_result.reading_time_minutes % 60}m" 
                                 if analysis_result.reading_time_minutes >= 60 
                                 else f"{analysis_result.reading_time_minutes}m"
            },
            "complexity": {
                "score": analysis_result.complexity_score,
                "level": "简单" if analysis_result.complexity_score < 30 
                        else "中等" if analysis_result.complexity_score < 60 
                        else "复杂"
            }
        }

    def _count_all_sections(self, sections: List[Section]) -> int:
        """统计所有章节数量"""
        count = len(sections)
        for section in sections:
            count += self._count_all_sections(section.subsections)
        return count

    def get_flat_sections(self, analysis_result: AnalysisResult) -> List[Dict[str, Any]]:
        """获取扁平化的章节列表"""
        flat_list = []
        
        def flatten(sections, prefix=""):
            for i, section in enumerate(sections):
                current_prefix = f"{prefix}{i + 1}."
                flat_list.append({
                    "number": current_prefix,
                    "title": section.title,
                    "level": section.level,
                    "word_count": section.word_count,
                    "paragraph_count": section.paragraph_count,
                    "line_range": f"{section.start_line}-{section.end_line}",
                    "has_subsections": len(section.subsections) > 0
                })
                flatten(section.subsections, current_prefix)
        
        flatten(analysis_result.sections)
        return flat_list
