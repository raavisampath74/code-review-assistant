"""
Security Agent Module
CrewAI agent for vulnerability and security checks.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass

try:
    from crewai import Agent, Task, Crew
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False


@dataclass
class SecurityAgentConfig:
    """Configuration for the security agent."""
    role: str = "Security Analyst"
    goal: str = "Identify security vulnerabilities and potential risks in code"
    backstory: str = """You are a cybersecurity expert specializing in secure code review.
    You have deep knowledge of OWASP Top 10, secure coding practices, and common vulnerability patterns."""
    verbose: bool = True
    allow_delegation: bool = False


# Common security patterns to detect
SECURITY_PATTERNS = {
    "sql_injection": ["execute(", "executemany(", "raw(", "cursor.execute"],
    "xss": ["innerHTML", "document.write", "eval("],
    "hardcoded_secrets": ["password=", "api_key=", "secret=", "token="],
    "unsafe_deserialization": ["pickle.loads", "yaml.load(", "eval("],
    "path_traversal": ["open(", "../", "..\\"],
    "command_injection": ["os.system(", "subprocess.call(", "shell=True"]
}


class SecurityAgent:
    """Security-focused agent for vulnerability detection."""
    
    def __init__(self, config: Optional[SecurityAgentConfig] = None, llm: Optional[Any] = None):
        self.config = config or SecurityAgentConfig()
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
    
    def scan_for_vulnerabilities(self, code: str) -> Dict[str, Any]:
        """Scan code for common security vulnerabilities."""
        findings = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            for vuln_type, patterns in SECURITY_PATTERNS.items():
                for pattern in patterns:
                    if pattern in line:
                        findings.append({
                            "type": vuln_type,
                            "line": i,
                            "pattern": pattern,
                            "code": line.strip(),
                            "severity": self._get_severity(vuln_type)
                        })
        
        return {"findings": findings, "total": len(findings)}
    
    def _get_severity(self, vuln_type: str) -> str:
        high_severity = ["sql_injection", "command_injection", "unsafe_deserialization"]
        return "HIGH" if vuln_type in high_severity else "MEDIUM"
    
    def review(self, code: str) -> Dict[str, Any]:
        """Perform security review."""
        static_scan = self.scan_for_vulnerabilities(code)
        
        if not CREWAI_AVAILABLE:
            return {"status": "partial", "static_analysis": static_scan}
        
        task = Task(
            description=f"Analyze this code for security vulnerabilities:\n```python\n{code}\n```",
            agent=self.agent,
            expected_output="Security findings with severity and remediation"
        )
        
        crew = Crew(agents=[self.agent], tasks=[task], verbose=True)
        result = crew.kickoff()
        
        return {"status": "success", "static_analysis": static_scan, "ai_review": str(result)}


def create_security_agent(llm: Optional[Any] = None) -> SecurityAgent:
    return SecurityAgent(llm=llm)
