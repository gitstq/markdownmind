"""Tests for Markdown parser module"""

import pytest
from markdownmind.parser import MarkdownParser, NodeType, DocumentNode


class TestMarkdownParser:
    """Test MarkdownParser class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = MarkdownParser()

    def test_parse_empty_content(self):
        """Test parsing empty content"""
        result = self.parser.parse("")
        assert len(result.nodes) == 0
        assert result.statistics["total_lines"] == 0

    def test_parse_heading(self):
        """Test parsing headings"""
        content = "# Heading 1\n## Heading 2\n### Heading 3"
        result = self.parser.parse(content)
        
        assert len(result.nodes) == 3
        assert result.nodes[0].type == NodeType.HEADING
        assert result.nodes[0].level == 1
        assert result.nodes[0].content == "Heading 1"
        assert result.nodes[1].level == 2
        assert result.nodes[2].level == 3

    def test_parse_paragraph(self):
        """Test parsing paragraphs"""
        content = "This is a paragraph.\n\nThis is another paragraph."
        result = self.parser.parse(content)
        
        assert result.nodes[0].type == NodeType.PARAGRAPH
        assert result.nodes[0].content == "This is a paragraph."

    def test_parse_code_block(self):
        """Test parsing code blocks"""
        content = """```python
def hello():
    print("Hello")
```"""
        result = self.parser.parse(content)
        
        assert len(result.nodes) == 1
        assert result.nodes[0].type == NodeType.CODE_BLOCK
        assert result.nodes[0].metadata["language"] == "python"
        assert "def hello():" in result.nodes[0].content

    def test_parse_list_items(self):
        """Test parsing list items"""
        content = "- Item 1\n- Item 2\n- Item 3"
        result = self.parser.parse(content)
        
        assert len(result.nodes) == 3
        assert all(n.type == NodeType.LIST_ITEM for n in result.nodes)
        assert result.nodes[0].content == "Item 1"

    def test_parse_quote(self):
        """Test parsing blockquotes"""
        content = "> This is a quote"
        result = self.parser.parse(content)
        
        assert len(result.nodes) == 1
        assert result.nodes[0].type == NodeType.QUOTE
        assert result.nodes[0].content == "This is a quote"

    def test_parse_front_matter(self):
        """Test parsing YAML front matter"""
        content = """---
title: Test Document
author: Test Author
date: 2024-01-01
tags: [test, markdown]
---

# Content

This is the content."""
        result = self.parser.parse(content)
        
        assert result.meta.title == "Test Document"
        assert result.meta.author == "Test Author"
        assert result.meta.date == "2024-01-01"
        assert result.meta.tags == ["test", "markdown"]

    def test_statistics_calculation(self):
        """Test statistics calculation"""
        content = """# Title

This is a paragraph with some words.

```python
code block
```

- List item 1
- List item 2

> A quote"""
        result = self.parser.parse(content)
        
        assert result.statistics["heading_count"] == 1
        assert result.statistics["paragraph_count"] == 1
        assert result.statistics["code_block_count"] == 1
        assert result.statistics["list_item_count"] == 2
        assert result.statistics["quote_count"] == 1
        assert result.statistics["word_count"] > 0

    def test_extract_headings(self):
        """Test extracting headings"""
        content = "# H1\n## H2\n### H3"
        result = self.parser.parse(content)
        headings = self.parser.extract_headings(result)
        
        assert len(headings) == 3
        assert headings[0]["level"] == 1
        assert headings[0]["content"] == "H1"

    def test_extract_links(self):
        """Test extracting links"""
        content = "[Link1](http://example.com) and [Link2](http://test.com)"
        result = self.parser.parse(content)
        links = self.parser.extract_links(result)
        
        assert len(links) == 2
        assert links[0]["text"] == "Link1"
        assert links[0]["url"] == "http://example.com"

    def test_extract_images(self):
        """Test extracting images"""
        content = "![Alt text](image.png) and ![Another](photo.jpg)"
        result = self.parser.parse(content)
        images = self.parser.extract_images(result)
        
        assert len(images) == 2
        assert images[0]["alt"] == "Alt text"
        assert images[0]["url"] == "image.png"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
