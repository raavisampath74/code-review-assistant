"""
Output Formatter Module
Formats the final review output for display.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class Severity(Enum):
    """Issue severity levels."""
    HIGH = "🔴 HIGH"
    MEDIUM = "🟡 MEDIUM"
    LOW = "🟢 LOW"


@dataclass
class ReviewIssue:
    """Represents a single review issue."""
    title: str
    description: str
    severity: Severity
    line_number: Optional[int]
    suggestion: str
    code_snippet: Optional[str] = None
    improved_code: Optional[str] = None
    category: str = "general"


@dataclass 
class ReviewReport:
    """Complete review report."""
    issues: List[ReviewIssue]
    summary: str
    overall_score: int  # 1-10
    improved_code: Optional[str] = None


class ReviewFormatter:
    """Formats review results for display."""
    
    @staticmethod
    def format_issue(issue: ReviewIssue) -> str:
        """Format a single issue for display."""
        output = []
        output.append(f"### {issue.severity.value} - {issue.title}")
        output.append(f"**Category:** {issue.category}")
        
        if issue.line_number:
            output.append(f"**Line:** {issue.line_number}")
        
        output.append(f"\n**Issue:** {issue.description}")
        output.append(f"\n**Suggestion:** {issue.suggestion}")
        
        if issue.code_snippet:
            output.append(f"\n**Original Code:**\n```python\n{issue.code_snippet}\n```")
        
        if issue.improved_code:
            output.append(f"\n**Improved Code:**\n```python\n{issue.improved_code}\n```")
        
        output.append("\n---")
        return "\n".join(output)
    
    @staticmethod
    def format_report(report: ReviewReport) -> str:
        """Format complete review report."""
        output = []
        
        # Header
        output.append("# 📋 Code Review Report\n")
        
        # Summary
        output.append(f"## Summary\n{report.summary}\n")
        
        # Score
        score_emoji = "🌟" if report.overall_score >= 8 else "⭐" if report.overall_score >= 5 else "💫"
        output.append(f"## Overall Score: {score_emoji} {report.overall_score}/10\n")
        
        # Issue Statistics
        high_count = sum(1 for i in report.issues if i.severity == Severity.HIGH)
        medium_count = sum(1 for i in report.issues if i.severity == Severity.MEDIUM)
        low_count = sum(1 for i in report.issues if i.severity == Severity.LOW)
        
        output.append("## Issue Statistics")
        output.append(f"- 🔴 High: {high_count}")
        output.append(f"- 🟡 Medium: {medium_count}")
        output.append(f"- 🟢 Low: {low_count}")
        output.append(f"- **Total:** {len(report.issues)}\n")
        
        # Detailed Issues
        output.append("## Detailed Issues\n")
        for issue in report.issues:
            output.append(ReviewFormatter.format_issue(issue))
        
        # Improved Code
        if report.improved_code:
            output.append("## 🛠️ Improved Code\n")
            output.append(f"```python\n{report.improved_code}\n```")
        
        return "\n".join(output)
    
    @staticmethod
    def format_for_download(report: ReviewReport) -> str:
        """Format report for text file download."""
        output = []
        output.append("=" * 60)
        output.append("CODE REVIEW REPORT")
        output.append("=" * 60)
        output.append("")
        output.append(f"SUMMARY: {report.summary}")
        output.append(f"OVERALL SCORE: {report.overall_score}/10")
        output.append("")
        output.append("-" * 60)
        output.append("ISSUES FOUND")
        output.append("-" * 60)
        
        for i, issue in enumerate(report.issues, 1):
            output.append(f"\n[Issue #{i}]")
            output.append(f"Severity: {issue.severity.name}")
            output.append(f"Category: {issue.category}")
            output.append(f"Title: {issue.title}")
            if issue.line_number:
                output.append(f"Line: {issue.line_number}")
            output.append(f"Description: {issue.description}")
            output.append(f"Suggestion: {issue.suggestion}")
            if issue.improved_code:
                output.append(f"Improved Code:\n{issue.improved_code}")
        
        if report.improved_code:
            output.append("")
            output.append("=" * 60)
            output.append("IMPROVED CODE")
            output.append("=" * 60)
            output.append(report.improved_code)
        
        return "\n".join(output)


def parse_llm_response(response: str) -> ReviewReport:
    """
    Parse LLM response into structured ReviewReport.
    
    Args:
        response: Raw LLM response text
        
    Returns:
        ReviewReport object
    """
    # This is a simplified parser - in production you'd want more robust parsing
    issues = []
    
    # Try to extract issues from the response
    lines = response.split("\n")
    current_issue = {}
    
    for line in lines:
        line = line.strip()
        if line.startswith("Issue:") or line.startswith("**Issue"):
            if current_issue:
                issues.append(_create_issue(current_issue))
            current_issue = {"title": line.replace("Issue:", "").replace("**", "").strip()}
        elif line.startswith("Severity:"):
            current_issue["severity"] = line.replace("Severity:", "").strip()
        elif line.startswith("Line:"):
            try:
                current_issue["line"] = int(line.replace("Line:", "").strip())
            except:
                pass
        elif line.startswith("Suggestion:"):
            current_issue["suggestion"] = line.replace("Suggestion:", "").strip()
        elif line.startswith("Category:"):
            current_issue["category"] = line.replace("Category:", "").strip()
    
    if current_issue:
        issues.append(_create_issue(current_issue))
    
    # If no structured issues found, create a general one
    if not issues:
        issues.append(ReviewIssue(
            title="Code Review Feedback",
            description=response[:500],
            severity=Severity.MEDIUM,
            line_number=None,
            suggestion="See detailed feedback above",
            category="general"
        ))
    
    return ReviewReport(
        issues=issues,
        summary=f"Found {len(issues)} issues in the code.",
        overall_score=max(1, 10 - len(issues))
    )


def _create_issue(data: dict) -> ReviewIssue:
    """Create ReviewIssue from parsed data."""
    severity_map = {
        "high": Severity.HIGH,
        "medium": Severity.MEDIUM,
        "low": Severity.LOW
    }
    
    severity_str = data.get("severity", "medium").lower()
    severity = severity_map.get(severity_str, Severity.MEDIUM)
    
    return ReviewIssue(
        title=data.get("title", "Unnamed Issue"),
        description=data.get("description", ""),
        severity=severity,
        line_number=data.get("line"),
        suggestion=data.get("suggestion", "Review this code section"),
        category=data.get("category", "general")
    )
