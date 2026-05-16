"""Tests for document scorer module"""

import pytest
from markdownmind.parser import MarkdownParser
from markdownmind.analyzer import DocumentAnalyzer
from markdownmind.scorer import DocumentScorer


class TestDocumentScorer:
    """Test DocumentScorer class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = MarkdownParser()
        self.analyzer = DocumentAnalyzer()
        self.scorer = DocumentScorer()

    def test_score_simple_document(self):
        """Test scoring a simple document"""
        content = """---
title: Test Document
description: A test document
---

# Introduction

This is a well-structured document.

## Section 1

Content here.

## Section 2

More content.

# Conclusion

Summary here."""
        
        parse_result = self.parser.parse(content)
        analysis = self.analyzer.analyze(parse_result)
        score = self.scorer.score(parse_result, analysis)
        
        assert 0 <= score.overall_score <= 100
        assert score.grade in ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D"]
        assert len(score.breakdown) == 5  # 5 categories

    def test_score_breakdown(self):
        """Test score breakdown"""
        content = "# Title\n\nSome content here."
        
        parse_result = self.parser.parse(content)
        analysis = self.analyzer.analyze(parse_result)
        score = self.scorer.score(parse_result, analysis)
        
        categories = [b.category for b in score.breakdown]
        assert "readability" in categories
        assert "completeness" in categories
        assert "consistency" in categories
        assert "structure" in categories
        assert "engagement" in categories

    def test_score_issues(self):
        """Test issue detection"""
        # Document with issues
        content = """# Title

This is a very long sentence that goes on and on without any breaks or proper punctuation making it difficult to read and understand what the author is trying to convey to the reader."""
        
        parse_result = self.parser.parse(content)
        analysis = self.analyzer.analyze(parse_result)
        score = self.scorer.score(parse_result, analysis)
        
        # Should have issues
        assert len(score.issues) > 0

    def test_score_strengths(self):
        """Test strength detection"""
        content = """---
title: Good Document
description: Well structured
---

# Introduction

This is good content.

## Section 1

More good content.

# Conclusion

Final thoughts."""
        
        parse_result = self.parser.parse(content)
        analysis = self.analyzer.analyze(parse_result)
        score = self.scorer.score(parse_result, analysis)
        
        # Good document should have strengths
        assert len(score.strengths) > 0

    def test_grade_calculation(self):
        """Test grade calculation"""
        content = "# Title\n\nContent."
        
        parse_result = self.parser.parse(content)
        analysis = self.analyzer.analyze(parse_result)
        score = self.scorer.score(parse_result, analysis)
        
        # Verify grade based on score
        if score.overall_score >= 90:
            assert score.grade == "A+"
        elif score.overall_score >= 85:
            assert score.grade == "A"
        elif score.overall_score >= 80:
            assert score.grade == "A-"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
