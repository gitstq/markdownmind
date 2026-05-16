#!/usr/bin/env python3
"""
MarkdownMind - 命令行界面

轻量级Markdown文档智能处理工具
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional

import click

from . import __version__
from .parser import MarkdownParser
from .analyzer import DocumentAnalyzer
from .scorer import DocumentScorer
from .outline import OutlineGenerator, OutlineFormat
from .diff import DocumentDiff
from .formatter import OutputFormatter


# ASCII Art Logo
LOGO = """
╔═══════════════════════════════════════════════════════════╗
║  ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗██████╗  ██████╗ ██╗  ║
║  ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝██╔══██╗██╔═══██╗██║  ║
║  ██╔████╔██║███████║██║  ██║█████╔╝ ██║  ██║██║   ██║██║  ║
║  ██║╚██╔╝██║██╔══██║██║  ██║██╔═██╗ ██║  ██║██║   ██║██║  ║
║  ██║ ╚═╝ ██║██║  ██║██████╔╝██║  ██╗██████╔╝╚██████╔╝███████╗
║  ╚═╝     ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚══════╝
╚═══════════════════════════════════════════════════════════╝
"""


@click.group(invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, help='显示版本信息')
@click.pass_context
def cli(ctx, version):
    """MarkdownMind - 轻量级Markdown文档智能处理工具"""
    if version:
        click.echo(f"MarkdownMind v{__version__}")
        sys.exit(0)
    
    if ctx.invoked_subcommand is None:
        click.echo(LOGO)
        click.echo("使用 markdownmind --help 查看帮助信息\n")


@cli.command()
@click.argument('file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='输出文件路径')
@click.option('--format', '-f', 'fmt', type=click.Choice(['terminal', 'json', 'html']), 
              default='terminal', help='输出格式')
@click.option('--no-color', is_flag=True, help='禁用彩色输出')
def analyze(file: Path, output: Optional[Path], fmt: str, no_color: bool):
    """分析Markdown文档结构和质量"""
    formatter = OutputFormatter(use_color=not no_color)
    
    try:
        # 解析文档
        parser = MarkdownParser()
        parse_result = parser.parse_file(str(file))
        
        # 分析文档
        analyzer = DocumentAnalyzer()
        analysis_result = analyzer.analyze(parse_result)
        
        # 评分
        scorer = DocumentScorer()
        score_result = scorer.score(parse_result, analysis_result)
        
        # 生成输出
        if fmt == 'json':
            data = {
                "file": str(file),
                "metadata": {
                    "title": parse_result.meta.title,
                    "author": parse_result.meta.author,
                    "date": parse_result.meta.date,
                    "description": parse_result.meta.description,
                },
                "statistics": parse_result.statistics,
                "analysis": analysis_result.statistics,
                "score": {
                    "overall": score_result.overall_score,
                    "grade": score_result.grade,
                    "breakdown": [
                        {
                            "category": b.category,
                            "score": b.score,
                            "weight": b.weight,
                            "details": b.details
                        }
                        for b in score_result.breakdown
                    ]
                },
                "recommendations": analysis_result.recommendations,
            }
            result = formatter.to_json(data)
        elif fmt == 'html':
            result = formatter.to_html_report(parse_result, analysis_result, score_result)
        else:
            # 终端输出
            result = formatter.format_analysis(parse_result, analysis_result)
            result += "\n"
            result += formatter.format_score(score_result)
        
        # 输出结果
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result)
            click.echo(f"✅ 分析报告已保存到: {output}")
        else:
            click.echo(result)
            
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='输出文件路径')
@click.option('--format', '-f', 'fmt', type=click.Choice(['markdown', 'json', 'mermaid', 'html', 'text', 'yaml']),
              default='markdown', help='输出格式')
@click.option('--stats/--no-stats', default=True, help='是否包含统计信息')
def outline(file: Path, output: Optional[Path], fmt: str, stats: bool):
    """生成文档大纲"""
    try:
        # 解析文档
        parser = MarkdownParser()
        parse_result = parser.parse_file(str(file))
        
        # 分析文档
        analyzer = DocumentAnalyzer()
        analysis_result = analyzer.analyze(parse_result)
        
        # 生成大纲
        generator = OutlineGenerator()
        
        format_map = {
            'markdown': OutlineFormat.MARKDOWN,
            'json': OutlineFormat.JSON,
            'mermaid': OutlineFormat.MERMAID,
            'html': OutlineFormat.HTML,
            'text': OutlineFormat.TEXT,
            'yaml': OutlineFormat.YAML,
        }
        
        result = generator.generate(analysis_result, format_map[fmt])
        
        # 添加摘要
        if stats and fmt == 'markdown':
            summary = generator.generate_summary(parse_result, analysis_result)
            result = summary + "\n" + result
        
        # 输出结果
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result)
            click.echo(f"✅ 大纲已保存到: {output}")
        else:
            click.echo(result)
            
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('old_file', type=click.Path(exists=True, path_type=Path))
@click.argument('new_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='输出文件路径')
@click.option('--format', '-f', 'fmt', type=click.Choice(['summary', 'unified', 'colored', 'html']),
              default='summary', help='输出格式')
def diff(old_file: Path, new_file: Path, output: Optional[Path], fmt: str):
    """对比两个Markdown文档的差异"""
    formatter = OutputFormatter()
    
    try:
        differ = DocumentDiff()
        
        if fmt == 'summary':
            result = differ.compare_files(str(old_file), str(new_file))
            output_text = formatter.format_diff_summary(result)
        elif fmt == 'unified':
            with open(old_file, 'r', encoding='utf-8') as f:
                old_content = f.read()
            with open(new_file, 'r', encoding='utf-8') as f:
                new_content = f.read()
            output_text = differ.generate_unified_diff(
                old_content, new_content,
                old_name=str(old_file.name),
                new_name=str(new_file.name)
            )
        elif fmt == 'colored':
            with open(old_file, 'r', encoding='utf-8') as f:
                old_content = f.read()
            with open(new_file, 'r', encoding='utf-8') as f:
                new_content = f.read()
            output_text = differ.generate_colored_diff(old_content, new_content)
        elif fmt == 'html':
            with open(old_file, 'r', encoding='utf-8') as f:
                old_content = f.read()
            with open(new_file, 'r', encoding='utf-8') as f:
                new_content = f.read()
            output_text = differ.generate_html_diff(old_content, new_content)
        else:
            output_text = "未知格式"
        
        # 输出结果
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(output_text)
            click.echo(f"✅ 差异报告已保存到: {output}")
        else:
            click.echo(output_text)
            
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='输出文件路径')
@click.option('--format', '-f', 'fmt', type=click.Choice(['terminal', 'json']), 
              default='terminal', help='输出格式')
@click.option('--no-color', is_flag=True, help='禁用彩色输出')
def score(file: Path, output: Optional[Path], fmt: str, no_color: bool):
    """评估Markdown文档质量"""
    formatter = OutputFormatter(use_color=not no_color)
    
    try:
        # 解析文档
        parser = MarkdownParser()
        parse_result = parser.parse_file(str(file))
        
        # 分析文档
        analyzer = DocumentAnalyzer()
        analysis_result = analyzer.analyze(parse_result)
        
        # 评分
        scorer = DocumentScorer()
        score_result = scorer.score(parse_result, analysis_result)
        
        if fmt == 'json':
            data = {
                "file": str(file),
                "overall_score": score_result.overall_score,
                "grade": score_result.grade,
                "breakdown": [
                    {
                        "category": b.category,
                        "score": b.score,
                        "weight": b.weight,
                        "max_score": b.max_score,
                        "details": b.details
                    }
                    for b in score_result.breakdown
                ],
                "issues": score_result.issues,
                "strengths": score_result.strengths,
            }
            result = formatter.to_json(data)
        else:
            result = formatter.format_score(score_result)
        
        # 输出结果
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result)
            click.echo(f"✅ 评分报告已保存到: {output}")
        else:
            click.echo(result)
            
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('file', type=click.Path(exists=True, path_type=Path))
def stats(file: Path):
    """显示Markdown文档统计信息"""
    try:
        parser = MarkdownParser()
        result = parser.parse_file(str(file))
        
        click.echo(f"\n📄 {file.name}")
        click.echo("=" * 50)
        
        stats = result.statistics
        click.echo(f"总字数: {stats.get('word_count', 0):,}")
        click.echo(f"字符数: {stats.get('char_count', 0):,}")
        click.echo(f"总行数: {stats.get('total_lines', 0)}")
        click.echo(f"标题数: {stats.get('heading_count', 0)}")
        click.echo(f"段落数: {stats.get('paragraph_count', 0)}")
        click.echo(f"代码块: {stats.get('code_block_count', 0)}")
        click.echo(f"列表项: {stats.get('list_item_count', 0)}")
        click.echo(f"引用块: {stats.get('quote_count', 0)}")
        click.echo(f"链接数: {stats.get('link_count', 0)}")
        click.echo(f"图片数: {stats.get('image_count', 0)}")
        
        if result.meta.title:
            click.echo(f"\n标题: {result.meta.title}")
        if result.meta.author:
            click.echo(f"作者: {result.meta.author}")
        
        click.echo("")
            
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('files', nargs=-1, required=True, type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='输出文件路径')
def batch(files: list, output: Optional[Path]):
    """批量分析多个Markdown文档"""
    try:
        results = []
        
        for file in files:
            parser = MarkdownParser()
            parse_result = parser.parse_file(str(file))
            
            analyzer = DocumentAnalyzer()
            analysis_result = analyzer.analyze(parse_result)
            
            scorer = DocumentScorer()
            score_result = scorer.score(parse_result, analysis_result)
            
            results.append({
                "file": str(file.name),
                "title": parse_result.meta.title or file.stem,
                "word_count": parse_result.statistics.get("word_count", 0),
                "score": score_result.overall_score,
                "grade": score_result.grade,
                "reading_time": analysis_result.reading_time_minutes,
            })
        
        # 输出表格
        click.echo("\n📊 批量分析结果")
        click.echo("=" * 80)
        click.echo(f"{'文件名':<30} {'标题':<20} {'字数':<10} {'评分':<8} {'等级':<6} {'阅读时间':<10}")
        click.echo("-" * 80)
        
        for r in results:
            title = r['title'][:18] + ".." if len(r['title']) > 20 else r['title']
            click.echo(f"{r['file']:<30} {title:<20} {r['word_count']:<10,} {r['score']:<8.1f} {r['grade']:<6} {r['reading_time']}m")
        
        click.echo("=" * 80)
        
        # 保存JSON
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            click.echo(f"\n✅ 结果已保存到: {output}")
        
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


def main():
    """主入口"""
    cli()


if __name__ == '__main__':
    main()
