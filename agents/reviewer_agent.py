"""
Reviewer Agent Module
CrewAI agent for static analysis and logic review.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass

try:
    from crewai import Agent, Task, Crew
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False


@dataclass
class ReviewerAgentConfig:
    """Configuration for the reviewer agent."""
    role: str = "Senior Code Reviewer"
    goal: str = "Analyze code for quality, readability, maintainability, and best practices"
    backstory: str = """You are a senior software engineer with 15+ years of experience 
    in code review. You have worked at top tech companies and have a deep understanding 
    of software engineering best practices, design patterns, and clean code principles."""
    verbose: bool = True
    allow_delegation: bool = False


class ReviewerAgent:
    """Code reviewer agent using CrewAI for intelligent code analysis."""
    
    def __init__(self, config: Optional[ReviewerAgentConfig] = None, llm: Optional[Any] = None):
        self.config = config or ReviewerAgentConfig()
        self.llm = llm
        
        if CREWAI_AVAILABLE:
            self.agent = Agent(
                role=self.config.role,
                goal=self.config.goal,
                backstory=self.config.backstory,
                verbose=self.config.verbose,
                allow_delegation=self.config.allow_delegation,
                llm=llm
            )
        else:
            self.agent = None
    
    def create_review_task(self, code: str, focus: str = "general") -> Optional[Any]:
        """Create a code review task."""
        if not CREWAI_AVAILABLE:
            return None
        
        task_descriptions = {
            "general": f"""
            Perform a comprehensive code review:
            ```python
            {code}
            ```
            
            Analyze: code quality, naming, function design, error handling, edge cases.
            """,
            "logic": f"""
            Analyze logic and algorithms:
            ```python
            {code}
            ```
            
            Focus: algorithm correctness, edge cases, bugs, logic flow.
            """,
            "style": f"""
            Review code style:
            ```python
            {code}
            ```
            
            Check: PEP8 compliance, naming conventions, organization, comments.
            """
        }
        
        description = task_descriptions.get(focus, task_descriptions["general"])
        
        return Task(
            description=description,
            agent=self.agent,
            expected_output="Detailed code review with issues, suggestions, and improved code"
        )
    
    def review(self, code: str, focus: str = "general") -> Dict[str, Any]:
        """Perform code review using the agent."""
        if not CREWAI_AVAILABLE:
            return {
                "status": "fallback",
                "message": "CrewAI not available",
                "review": self._fallback_review(code)
            }
        
        task = self.create_review_task(code, focus)
        crew = Crew(agents=[self.agent], tasks=[task], verbose=True)
        result = crew.kickoff()
        
        return {"status": "success", "review": str(result), "focus": focus}
    
    def _fallback_review(self, code: str) -> str:
        """Basic review without CrewAI."""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append(f"Line {i}: Line too long ({len(line)} chars)")
            if line.endswith(' '):
                issues.append(f"Line {i}: Trailing whitespace")
            if 'TODO' in line or 'FIXME' in line:
                issues.append(f"Line {i}: Contains TODO/FIXME")
        
        return "\n".join(issues) if issues else "No obvious issues found."


def create_reviewer_agent(llm: Optional[Any] = None) -> ReviewerAgent:
    return ReviewerAgent(llm=llm)
