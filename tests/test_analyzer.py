"""Tests for document analyzer module"""

import pytest
from markdownmind.parser import MarkdownParser
from markdownmind.analyzer import DocumentAnalyzer, Section


class TestDocumentAnalyzer:
    """Test DocumentAnalyzer class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = MarkdownParser()
        self.analyzer = DocumentAnalyzer()

    def test_analyze_simple_document(self):
        """Test analyzing a simple document"""
        content = """# Title

This is a paragraph.

## Section 1

Content of section 1.

## Section 2

Content of section 2."""
        
        parse_result = self.parser.parse(content)
        analysis = self.analyzer.analyze(parse_result)
        
        assert analysis.structure_depth == 2
        assert len(analysis.sections) == 1  # Title section with subsections
        assert len(analysis.sections[0].subsections) == 2

    def test_analyze_structure_depth(self):
        """Test structure depth calculation"""
        content = """# H1
## H2
### H3
#### H4"""
        
        parse_result = self.parser.parse(content)
        analysis = self.analyzer.analyze(parse_result)
        
        assert analysis.structure_depth == 4

    def test_reading_time_calculation(self):
        """Test reading time estimation"""
        # Create content with ~200 words
        content = "# Title\n\n" + "word " * 200
        
        parse_result = self.parser.parse(content)
        analysis = self.analyzer.analyze(parse_result)
        
        # Should be around 1 minute
        assert analysis.reading_time_minutes >= 1

    def test_balance_score(self):
        """Test structure balance score"""
        content = """# Title

## Section 1

Short.

## Section 2

This is a much longer section with many more words to create imbalance in the document structure."""
        
        parse_result = self.parser.parse(content)
        analysis = self.analyzer.analyze(parse_result)
        
        # Should be less than 100 due to imbalance
        assert analysis.structure_balance_score < 100

    def test_recommendations(self):
        """Test recommendations generation"""
        # Document with potential issues
        content = """# Title

""" + "word " * 2000  # Long content without subsections
        
        parse_result = self.parser.parse(content)
        analysis = self.analyzer.analyze(parse_result)
        
        # Should have recommendations
        assert len(analysis.recommendations) > 0

    def test_complexity_score(self):
        """Test complexity score calculation"""
        content = """# Title
## Section 1
### Subsection 1
#### Deep section

Some content here."""
        
        parse_result = self.parser.parse(content)
        analysis = self.analyzer.analyze(parse_result)
        
        # Deep structure should increase complexity
        assert analysis.complexity_score > 0

    def test_get_flat_sections(self):
        """Test getting flat section list"""
        content = """# Title
## Section 1
### Subsection 1
## Section 2"""
        
        parse_result = self.parser.parse(content)
        analysis = self.analyzer.analyze(parse_result)
        flat_sections = self.analyzer.get_flat_sections(analysis)
        
        assert len(flat_sections) == 4  # Title + 2 sections + 1 subsection


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
