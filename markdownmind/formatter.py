"""
输出格式化模块

提供各种格式的分析结果输出，包括终端彩色输出、JSON、HTML等。
"""

import json
from typing import Dict, Any, List
from datetime import datetime

from .parser import ParseResult
from .analyzer import AnalysisResult
from .scorer import ScoreResult


class OutputFormatter:
    """输出格式化器"""

    # ANSI颜色代码
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "bright_red": "\033[91m",
        "bright_green": "\033[92m",
        "bright_yellow": "\033[93m",
        "bright_blue": "\033[94m",
    }

    def __init__(self, use_color: bool = True):
        self.use_color = use_color

    def _color(self, text: str, color: str) -> str:
        """添加颜色"""
        if not self.use_color:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def format_analysis(self, parse_result: ParseResult, 
                       analysis_result: AnalysisResult) -> str:
        """格式化分析结果"""
        lines = []
        
        # 标题
        lines.append(self._color("=" * 60, "cyan"))
        lines.append(self._color("📄 Markdown文档分析报告", "bold"))
        lines.append(self._color("=" * 60, "cyan"))
        lines.append("")
        
        # 元数据
        meta = parse_result.meta
        if meta.title or meta.author:
            lines.append(self._color("📋 文档信息", "bold"))
            if meta.title:
                lines.append(f"  标题: {meta.title}")
            if meta.author:
                lines.append(f"  作者: {meta.author}")
            if meta.date:
                lines.append(f"  日期: {meta.date}")
            if meta.description:
                lines.append(f"  描述: {meta.description}")
            lines.append("")
        
        # 基本统计
        stats = parse_result.statistics
        lines.append(self._color("📊 基本统计", "bold"))
        lines.append(f"  总字数: {stats.get('word_count', 0):,}")
        lines.append(f"  字符数: {stats.get('char_count', 0):,}")
        lines.append(f"  标题数: {stats.get('heading_count', 0)}")
        lines.append(f"  段落数: {stats.get('paragraph_count', 0)}")
        lines.append(f"  代码块: {stats.get('code_block_count', 0)}")
        lines.append(f"  列表项: {stats.get('list_item_count', 0)}")
        lines.append(f"  引用块: {stats.get('quote_count', 0)}")
        lines.append(f"  链接数: {stats.get('link_count', 0)}")
        lines.append(f"  图片数: {stats.get('image_count', 0)}")
        lines.append("")
        
        # 结构分析
        lines.append(self._color("🏗️ 结构分析", "bold"))
        lines.append(f"  结构深度: {analysis_result.structure_depth} 层")
        lines.append(f"  平均章节长度: {analysis_result.avg_section_length:.0f} 字")
        lines.append(f"  结构平衡性: {analysis_result.structure_balance_score}%")
        lines.append("")
        
        # 阅读时间
        lines.append(self._color("⏱️ 阅读信息", "bold"))
        minutes = analysis_result.reading_time_minutes
        if minutes >= 60:
            lines.append(f"  预计阅读时间: {minutes // 60}小时{minutes % 60}分钟")
        else:
            lines.append(f"  预计阅读时间: {minutes}分钟")
        lines.append("")
        
        # 复杂度
        complexity = analysis_result.complexity_score
        if complexity < 30:
            level = self._color("简单", "green")
        elif complexity < 60:
            level = self._color("中等", "yellow")
        else:
            level = self._color("复杂", "red")
        lines.append(self._color("📈 复杂度分析", "bold"))
        lines.append(f"  复杂度评分: {complexity}/100")
        lines.append(f"  复杂度等级: {level}")
        lines.append("")
        
        # 建议
        if analysis_result.recommendations:
            lines.append(self._color("💡 改进建议", "bold"))
            for rec in analysis_result.recommendations:
                lines.append(f"  • {rec}")
            lines.append("")
        
        lines.append(self._color("=" * 60, "cyan"))
        
        return "\n".join(lines)

    def format_score(self, score_result: ScoreResult) -> str:
        """格式化评分结果"""
        lines = []
        
        # 标题
        lines.append(self._color("=" * 60, "green"))
        lines.append(self._color("⭐ 文档质量评分", "bold"))
        lines.append(self._color("=" * 60, "green"))
        lines.append("")
        
        # 总分
        score = score_result.overall_score
        if score >= 80:
            color = "bright_green"
            emoji = "🌟"
        elif score >= 60:
            color = "bright_yellow"
            emoji = "⭐"
        else:
            color = "bright_red"
            emoji = "⚠️"
        
        lines.append(f"{emoji} {self._color('综合评分', 'bold')}: {self._color(f'{score}/100', color)} {self._color(f'({score_result.grade})', color)}")
        lines.append("")
        
        # 分项评分
        lines.append(self._color("📊 分项评分", "bold"))
        for item in score_result.breakdown:
            score_color = "green" if item.score >= 80 else "yellow" if item.score >= 60 else "red"
            bar_length = int(item.score / 5)  # 20字符宽度
            bar = "█" * bar_length + "░" * (20 - bar_length)
            lines.append(f"  {item.category:15} {self._color(bar, score_color)} {item.score:.1f}")
        lines.append("")
        
        # 优点
        if score_result.strengths:
            lines.append(self._color("✅ 文档亮点", "bold"))
            for strength in score_result.strengths[:5]:
                lines.append(f"  ✓ {strength}")
            lines.append("")
        
        # 问题
        if score_result.issues:
            lines.append(self._color("⚠️ 需要改进", "bold"))
            for issue in score_result.issues[:5]:
                lines.append(f"  • {issue}")
            lines.append("")
        
        lines.append(self._color("=" * 60, "green"))
        
        return "\n".join(lines)

    def format_diff_summary(self, diff_result) -> str:
        """格式化差异摘要"""
        lines = []
        
        lines.append(self._color("=" * 60, "magenta"))
        lines.append(self._color("📝 文档差异对比", "bold"))
        lines.append(self._color("=" * 60, "magenta"))
        lines.append("")
        
        stats = diff_result.statistics
        changes = stats.get("changes", {})
        
        # 行数变化
        added = changes.get("added_lines", 0)
        removed = changes.get("removed_lines", 0)
        net = changes.get("net_change", 0)
        
        lines.append(self._color("📊 变更统计", "bold"))
        lines.append(f"  新增行数: {self._color(f'+{added}', 'green')}")
        lines.append(f"  删除行数: {self._color(f'-{removed}', 'red')}")
        lines.append(f"  净变化: {self._color(f'{net:+d}', 'blue')}")
        
        # 字数变化
        word_change = changes.get("word_count_change", 0)
        if word_change != 0:
            color = "green" if word_change > 0 else "red"
            lines.append(f"  字数变化: {self._color(f'{word_change:+d}', color)}")
        
        # 结构变化
        structure_changes = changes.get("structure_changes", 0)
        if structure_changes > 0:
            lines.append(f"  结构变更: {structure_changes} 处")
        
        lines.append("")
        lines.append(self._color("=" * 60, "magenta"))
        
        return "\n".join(lines)

    def to_json(self, data: Dict[str, Any]) -> str:
        """输出JSON格式"""
        return json.dumps(data, ensure_ascii=False, indent=2)

    def to_html_report(self, parse_result: ParseResult,
                       analysis_result: AnalysisResult,
                       score_result: ScoreResult = None) -> str:
        """生成HTML报告"""
        html = [
            "<!DOCTYPE html>",
            "<html lang=\"zh-CN\">",
            "<head>",
            '  <meta charset="UTF-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            "  <title>MarkdownMind - 文档分析报告</title>",
            "  <style>",
            "    * { margin: 0; padding: 0; box-sizing: border-box; }",
            "    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #333; line-height: 1.6; }",
            "    .container { max-width: 900px; margin: 40px auto; padding: 0 20px; }",
            "    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 12px; margin-bottom: 30px; }",
            "    .header h1 { font-size: 2em; margin-bottom: 10px; }",
            "    .header p { opacity: 0.9; }",
            "    .card { background: white; border-radius: 12px; padding: 30px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }",
            "    .card h2 { color: #667eea; margin-bottom: 20px; font-size: 1.5em; }",
            "    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }",
            "    .stat-item { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }",
            "    .stat-value { font-size: 1.8em; font-weight: bold; color: #667eea; }",
            "    .stat-label { color: #666; font-size: 0.9em; margin-top: 5px; }",
            "    .score-circle { width: 120px; height: 120px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; font-size: 2em; font-weight: bold; }",
            "    .score-excellent { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; }",
            "    .score-good { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }",
            "    .score-average { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }",
            "    .score-poor { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; }",
            "    .recommendation { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0; border-radius: 4px; }",
            "    .footer { text-align: center; color: #666; margin-top: 40px; padding: 20px; }",
            "  </style>",
            "</head>",
            "<body>",
            '  <div class="container">',
            '    <div class="header">',
            "      <h1>📄 MarkdownMind</h1>",
            "      <p>智能文档分析报告</p>",
            "    </div>",
        ]
        
        # 评分卡片
        if score_result:
            score_class = "score-excellent" if score_result.overall_score >= 80 else \
                         "score-good" if score_result.overall_score >= 70 else \
                         "score-average" if score_result.overall_score >= 60 else "score-poor"
            html.extend([
                '    <div class="card">',
                '      <h2>⭐ 质量评分</h2>',
                f'      <div class="score-circle {score_class}">{score_result.overall_score:.0f}</div>',
                f'      <p style="text-align: center; color: #666;">等级: <strong>{score_result.grade}</strong></p>',
                "    </div>",
            ])
        
        # 统计卡片
        stats = parse_result.statistics
        html.extend([
            '    <div class="card">',
            '      <h2>📊 文档统计</h2>',
            '      <div class="stats-grid">',
            f'        <div class="stat-item"><div class="stat-value">{stats.get("word_count", 0):,}</div><div class="stat-label">字数</div></div>',
            f'        <div class="stat-item"><div class="stat-value">{stats.get("heading_count", 0)}</div><div class="stat-label">标题</div></div>',
            f'        <div class="stat-item"><div class="stat-value">{stats.get("paragraph_count", 0)}</div><div class="stat-label">段落</div></div>',
            f'        <div class="stat-item"><div class="stat-value">{stats.get("code_block_count", 0)}</div><div class="stat-label">代码块</div></div>',
            f'        <div class="stat-item"><div class="stat-value">{analysis_result.reading_time_minutes}m</div><div class="stat-label">阅读时间</div></div>',
            f'        <div class="stat-item"><div class="stat-value">{analysis_result.structure_depth}</div><div class="stat-label">结构深度</div></div>',
            "      </div>",
            "    </div>",
        ])
        
        # 建议卡片
        if analysis_result.recommendations:
            html.extend([
                '    <div class="card">',
                '      <h2>💡 改进建议</h2>',
            ])
            for rec in analysis_result.recommendations:
                html.append(f'      <div class="recommendation">{rec}</div>')
            html.extend([
                "    </div>",
            ])
        
        html.extend([
            '    <div class="footer">',
            f'      <p>Generated by MarkdownMind on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>',
            "    </div>",
            "  </div>",
            "</body>",
            "</html>",
        ])
        
        return "\n".join(html)
