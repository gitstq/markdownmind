"""
文档质量评分模块

提供可读性评分、完整性检查、一致性检测等质量评估功能。
"""

import re
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from collections import Counter

from .parser import ParseResult, NodeType
from .analyzer import AnalysisResult


@dataclass
class ScoreBreakdown:
    """评分细项"""
    category: str
    score: float
    weight: float
    max_score: float
    details: List[str] = field(default_factory=list)


@dataclass
class ScoreResult:
    """评分结果"""
    overall_score: float
    grade: str
    breakdown: List[ScoreBreakdown] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)


class DocumentScorer:
    """文档评分器"""

    # 评分权重配置
    DEFAULT_WEIGHTS = {
        "readability": 0.25,
        "completeness": 0.25,
        "consistency": 0.20,
        "structure": 0.15,
        "engagement": 0.15,
    }

    # 可读性等级边界
    READABILITY_LEVELS = {
        "very_easy": (90, 100, "非常容易"),
        "easy": (80, 89, "容易"),
        "fairly_easy": (70, 79, "较容易"),
        "standard": (60, 69, "标准"),
        "fairly_difficult": (50, 59, "较难"),
        "difficult": (30, 49, "困难"),
        "very_difficult": (0, 29, "非常困难"),
    }

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS

    def score(self, parse_result: ParseResult, analysis_result: AnalysisResult) -> ScoreResult:
        """
        对文档进行综合评分
        
        Args:
            parse_result: 解析结果
            analysis_result: 分析结果
            
        Returns:
            ScoreResult: 评分结果
        """
        result = ScoreResult(overall_score=0.0, grade="")
        
        # 各项评分
        readability = self._score_readability(parse_result)
        completeness = self._score_completeness(parse_result)
        consistency = self._score_consistency(parse_result)
        structure = self._score_structure(parse_result, analysis_result)
        engagement = self._score_engagement(parse_result)
        
        result.breakdown = [readability, completeness, consistency, structure, engagement]
        
        # 计算总分
        total_weight = sum(self.weights.values())
        weighted_sum = sum(
            b.score * self.weights.get(b.category, 0) 
            for b in result.breakdown
        )
        result.overall_score = round(weighted_sum / total_weight, 1)
        
        # 确定等级
        result.grade = self._get_grade(result.overall_score)
        
        # 收集问题和优点
        result.issues = self._collect_issues(result.breakdown)
        result.strengths = self._collect_strengths(result.breakdown)
        
        return result

    def _score_readability(self, parse_result: ParseResult) -> ScoreBreakdown:
        """可读性评分"""
        stats = parse_result.statistics
        details = []
        
        # 收集所有文本内容
        texts = []
        for node in parse_result.nodes:
            if node.type in (NodeType.PARAGRAPH, NodeType.QUOTE, NodeType.LIST_ITEM):
                texts.append(node.content)
        
        full_text = " ".join(texts)
        
        if not full_text:
            return ScoreBreakdown(
                category="readability",
                score=0,
                weight=self.weights["readability"],
                max_score=100,
                details=["文档内容为空"]
            )
        
        # 计算Flesch Reading Ease分数
        flesch_score = self._calculate_flesch_score(full_text)
        
        # 计算平均句长
        sentences = re.split(r'[.!?。！？]+', full_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_sentence_length = len(full_text.split()) / len(sentences) if sentences else 0
        
        # 计算平均词长
        words = full_text.split()
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
        
        # 评分转换 (Flesch分数转换为0-100)
        readability_score = max(0, min(100, flesch_score))
        
        # 根据句长调整
        if avg_sentence_length > 25:
            readability_score -= 10
            details.append(f"平均句长过长({avg_sentence_length:.1f}词)，建议拆分为短句")
        elif avg_sentence_length < 10:
            readability_score -= 5
            details.append("句子过短，可能缺乏连贯性")
        else:
            details.append(f"平均句长适中({avg_sentence_length:.1f}词)")
        
        # 根据词长调整
        if avg_word_length > 6:
            readability_score -= 5
            details.append("使用了较多长单词，可能影响可读性")
        
        details.append(f"Flesch可读性分数: {flesch_score:.1f} ({self._get_readability_level(flesch_score)})")
        
        return ScoreBreakdown(
            category="readability",
            score=max(0, readability_score),
            weight=self.weights["readability"],
            max_score=100,
            details=details
        )

    def _calculate_flesch_score(self, text: str) -> float:
        """计算Flesch Reading Ease分数"""
        # 简化版计算（针对中文和英文混合）
        sentences = re.split(r'[.!?。！？]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        words = text.split()
        word_count = len(words)
        
        # 音节估算（简化版）
        syllable_count = sum(self._estimate_syllables(w) for w in words)
        
        if sentence_count == 0 or word_count == 0:
            return 50  # 默认中等难度
        
        # Flesch Reading Ease公式
        score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)
        
        return score

    def _estimate_syllables(self, word: str) -> int:
        """估算单词音节数"""
        word = word.lower()
        # 移除标点
        word = re.sub(r'[^\w]', '', word)
        
        if not word:
            return 0
        
        # 简单估算：元音组数量
        vowels = 'aeiouy'
        syllables = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllables += 1
            prev_was_vowel = is_vowel
        
        # 确保至少一个音节
        return max(1, syllables)

    def _get_readability_level(self, score: float) -> str:
        """获取可读性等级描述"""
        for key, (min_score, max_score, desc) in self.READABILITY_LEVELS.items():
            if min_score <= score <= max_score:
                return desc
        return "未知"

    def _score_completeness(self, parse_result: ParseResult) -> ScoreBreakdown:
        """完整性评分"""
        stats = parse_result.statistics
        meta = parse_result.meta
        details = []
        score = 100
        
        # 检查元数据
        if not meta.title:
            score -= 15
            details.append("缺少文档标题")
        else:
            details.append(f"✓ 文档标题: {meta.title}")
        
        if not meta.description:
            score -= 10
            details.append("缺少文档描述")
        else:
            details.append("✓ 包含文档描述")
        
        # 检查必要章节
        headings = [node.content.lower() for node in parse_result.nodes if node.type == NodeType.HEADING]
        
        has_intro = any(h in ["介绍", "简介", "introduction", "概述", "overview"] for h in headings)
        has_conclusion = any(h in ["总结", "结论", "conclusion", "summary", "结语"] for h in headings)
        
        if not has_intro:
            score -= 10
            details.append("缺少介绍/简介章节")
        else:
            details.append("✓ 包含介绍章节")
        
        if not has_conclusion and stats.get("word_count", 0) > 500:
            score -= 5
            details.append("长文档缺少总结章节")
        elif has_conclusion:
            details.append("✓ 包含总结章节")
        
        # 检查内容量
        word_count = stats.get("word_count", 0)
        if word_count < 100:
            score -= 20
            details.append("文档内容过少")
        elif word_count < 300:
            score -= 10
            details.append("文档内容偏少")
        else:
            details.append(f"✓ 内容量适中({word_count}词)")
        
        # 检查代码说明
        code_blocks = stats.get("code_block_count", 0)
        if code_blocks > 0:
            # 检查代码块前后是否有说明
            code_with_context = 0
            for i, node in enumerate(parse_result.nodes):
                if node.type == NodeType.CODE_BLOCK:
                    has_before = i > 0 and parse_result.nodes[i-1].type == NodeType.PARAGRAPH
                    has_after = i < len(parse_result.nodes) - 1 and parse_result.nodes[i+1].type == NodeType.PARAGRAPH
                    if has_before or has_after:
                        code_with_context += 1
            
            if code_with_context < code_blocks:
                score -= 5
                details.append("部分代码块缺少说明文字")
            else:
                details.append("✓ 代码块都有相应说明")
        
        return ScoreBreakdown(
            category="completeness",
            score=max(0, score),
            weight=self.weights["completeness"],
            max_score=100,
            details=details
        )

    def _score_consistency(self, parse_result: ParseResult) -> ScoreBreakdown:
        """一致性评分"""
        details = []
        score = 100
        
        # 检查标题格式一致性
        headings = []
        for node in parse_result.nodes:
            if node.type == NodeType.HEADING:
                headings.append({
                    "level": node.level,
                    "content": node.content,
                    "has_punctuation": any(p in node.content for p in "。！？.")
                })
        
        if len(headings) >= 2:
            # 检查标点一致性
            with_punct = sum(1 for h in headings if h["has_punctuation"])
            if 0 < with_punct < len(headings):
                score -= 10
                details.append("标题标点使用不一致")
            else:
                details.append("✓ 标题格式一致")
            
            # 检查层级连续性
            levels = [h["level"] for h in headings]
            for i in range(1, len(levels)):
                if levels[i] > levels[i-1] + 1:
                    score -= 10
                    details.append(f"标题层级跳跃: 从H{levels[i-1]}直接到H{levels[i]}")
                    break
            else:
                details.append("✓ 标题层级连续")
        
        # 检查列表格式一致性
        list_items = [node for node in parse_result.nodes if node.type == NodeType.LIST_ITEM]
        if list_items:
            ordered_count = sum(1 for n in list_items if n.metadata.get("ordered"))
            if 0 < ordered_count < len(list_items):
                # 混合使用有序和无序列表，检查是否合理
                details.append("⚠ 同时使用了有序和无序列表")
            else:
                details.append("✓ 列表格式一致")
        
        # 检查代码块语言标注
        code_blocks = [node for node in parse_result.nodes if node.type == NodeType.CODE_BLOCK]
        if code_blocks:
            with_lang = sum(1 for n in code_blocks if n.metadata.get("language"))
            if with_lang < len(code_blocks):
                score -= 5
                details.append("部分代码块未标注语言")
            else:
                details.append("✓ 代码块语言标注完整")
        
        return ScoreBreakdown(
            category="consistency",
            score=max(0, score),
            weight=self.weights["consistency"],
            max_score=100,
            details=details
        )

    def _score_structure(self, parse_result: ParseResult, analysis_result: AnalysisResult) -> ScoreBreakdown:
        """结构评分"""
        details = []
        score = 100
        
        # 结构深度
        depth = analysis_result.structure_depth
        if depth > 4:
            score -= 15
            details.append(f"结构层级过深({depth}层)")
        elif depth < 2 and parse_result.statistics.get("word_count", 0) > 500:
            score -= 10
            details.append("内容较长但结构层次不足")
        else:
            details.append(f"✓ 结构层级合理({depth}层)")
        
        # 结构平衡性
        balance = analysis_result.structure_balance_score
        if balance < 50:
            score -= 15
            details.append(f"章节长度差异较大(平衡性{balance}%)")
        elif balance < 70:
            score -= 5
            details.append(f"章节长度略有差异(平衡性{balance}%)")
        else:
            details.append(f"✓ 章节长度分布均衡(平衡性{balance}%)")
        
        # 检查空章节
        empty_sections = 0
        for section in analysis_result.sections:
            if section.word_count < 50 and section.title != "(无标题)":
                empty_sections += 1
        
        if empty_sections > 0:
            score -= empty_sections * 5
            details.append(f"有{empty_sections}个章节内容过少")
        
        return ScoreBreakdown(
            category="structure",
            score=max(0, score),
            weight=self.weights["structure"],
            max_score=100,
            details=details
        )

    def _score_engagement(self, parse_result: ParseResult) -> ScoreBreakdown:
        """吸引力评分"""
        stats = parse_result.statistics
        details = []
        score = 100
        
        # 图片使用
        images = stats.get("image_count", 0)
        word_count = stats.get("word_count", 1)
        image_ratio = images / (word_count / 500)  # 每500字的图片数
        
        if images == 0:
            if word_count > 1000:
                score -= 15
                details.append("长文档缺少配图")
            else:
                score -= 5
                details.append("缺少配图")
        elif image_ratio < 0.5:
            details.append("配图较少")
        else:
            details.append(f"✓ 配图充足({images}张)")
        
        # 链接使用
        links = stats.get("link_count", 0)
        if links == 0:
            score -= 10
            details.append("缺少外部链接")
        else:
            details.append(f"✓ 包含{links}个外部链接")
        
        # 代码示例
        code_blocks = stats.get("code_block_count", 0)
        if code_blocks > 0:
            details.append(f"✓ 包含{code_blocks}个代码示例")
        
        # 列表使用（提升可读性）
        list_items = stats.get("list_item_count", 0)
        if list_items > 0:
            details.append(f"✓ 使用列表提升可读性({list_items}项)")
        
        # 引用使用
        quotes = stats.get("quote_count", 0)
        if quotes > 0:
            details.append(f"✓ 使用引用增强说服力({quotes}处)")
        
        return ScoreBreakdown(
            category="engagement",
            score=max(0, score),
            weight=self.weights["engagement"],
            max_score=100,
            details=details
        )

    def _get_grade(self, score: float) -> str:
        """根据分数获取等级"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        else:
            return "D"

    def _collect_issues(self, breakdowns: List[ScoreBreakdown]) -> List[str]:
        """收集问题列表"""
        issues = []
        for b in breakdowns:
            if b.score < 70:
                for detail in b.details:
                    if not detail.startswith("✓"):
                        issues.append(f"[{b.category}] {detail}")
        return issues[:10]  # 最多返回10个问题

    def _collect_strengths(self, breakdowns: List[ScoreBreakdown]) -> List[str]:
        """收集优点列表"""
        strengths = []
        for b in breakdowns:
            if b.score >= 80:
                for detail in b.details:
                    if detail.startswith("✓"):
                        strengths.append(f"[{b.category}] {detail[2:]}")
        return strengths[:10]  # 最多返回10个优点
