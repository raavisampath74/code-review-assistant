"""
AI-Powered Code Review Assistant
Entry point for the Streamlit application.
"""

import streamlit as st
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="AI Code Review Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --bg-dark: #0f0f23;
        --bg-card: #1a1a2e;
        --text-primary: #ffffff;
        --text-secondary: #a0aec0;
        --success: #48bb78;
        --warning: #f6ad55;
        --danger: #fc8181;
    }
    
    /* Light theme styling for better readability */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
    }
    
    /* Ensure text is dark and readable */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div {
        color: #1a1a2e !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a2e !important;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.8);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Card styling */
    .review-card {
        background: rgba(26, 26, 46, 0.9);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Severity badges */
    .severity-high {
        background: linear-gradient(135deg, #fc8181, #f56565);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    
    .severity-medium {
        background: linear-gradient(135deg, #f6ad55, #ed8936);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    
    .severity-low {
        background: linear-gradient(135deg, #48bb78, #38a169);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Code block styling */
    .stCodeBlock {
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Stats cards */
    .stat-card {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        color: #a0aec0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "review_history" not in st.session_state:
        st.session_state.review_history = []
    if "current_review" not in st.session_state:
        st.session_state.current_review = None
    if "api_key" not in st.session_state:
        st.session_state.api_key = os.getenv("OPENAI_API_KEY", "")


def render_header():
    """Render the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Code Review Assistant</h1>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar configuration."""
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.api_key,
            help="Enter your OpenAI API key"
        )
        st.session_state.api_key = api_key
        
        st.markdown("---")
        
        # Review Settings
        st.markdown("### 📋 Review Settings")
        
        review_type = st.selectbox(
            "Review Type",
            ["General", "Security", "Performance", "Readability"],
            help="Select the focus area for code review"
        )
        
        severity_filter = st.multiselect(
            "Severity Filter",
            ["HIGH", "MEDIUM", "LOW"],
            default=["HIGH", "MEDIUM", "LOW"]
        )
        
        use_rag = st.checkbox("Use RAG Context", value=True, help="Include knowledge base context")
        
        st.markdown("---")
        
        # LLM Settings
        st.markdown("### 🤖 LLM Settings")
        
        llm_provider = st.selectbox("LLM Provider", ["OpenAI", "Vertex AI"])
        
        temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
        
        st.markdown("---")
        
        # Stats
        st.markdown("### 📊 Session Stats")
        st.markdown(f"**Reviews:** {len(st.session_state.review_history)}")
        
        return {
            "review_type": review_type.lower(),
            "severity_filter": severity_filter,
            "use_rag": use_rag,
            "llm_provider": llm_provider.lower(),
            "temperature": temperature
        }


def render_code_input():
    """Render the code input section."""
    st.markdown("### 📝 Input Code")
    
    input_method = st.radio(
        "Input Method",
        ["Paste Code", "Upload File"],
        horizontal=True
    )
    
    code = ""
    
    if input_method == "Paste Code":
        code = st.text_area(
            "Paste your Python code here",
            height=300,
            placeholder="def example_function():\n    # Your code here\n    pass"
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload Python file",
            type=["py"],
            help="Upload a .py file for review"
        )
        if uploaded_file:
            code = uploaded_file.read().decode("utf-8")
            st.code(code, language="python")
    
    return code


def perform_review(code: str, settings: dict):
    """Perform the code review."""
    if not code.strip():
        st.warning("Please provide code to review.")
        return None
    
    # If no API key, use demo mode directly
    if not st.session_state.api_key:
        with st.spinner("🔍 Analyzing code (Demo Mode)..."):
            return create_demo_review(code, settings.get("review_type", "general"))
    
    with st.spinner("🔍 Analyzing code..."):
        try:
            from rag.rag_pipeline import create_rag_pipeline
            from utils.parser import parse_code
            
            # Parse the code
            chunks = parse_code(code)
            
            # Create RAG pipeline
            pipeline = create_rag_pipeline(
                llm_provider=settings["llm_provider"],
                api_key=st.session_state.api_key,
                temperature=settings["temperature"]
            )
            
            # Perform review
            result = pipeline.review_code(
                code=code,
                review_type=settings["review_type"],
                include_context=settings["use_rag"]
            )
            
            return result
            
        except Exception as e:
            st.error(f"Error during review: {str(e)}")
            # Return a mock result for demonstration
            return create_demo_review(code)


def create_demo_review(code: str, review_type: str = "general"):
    """Create a demonstration review with static analysis."""
    from utils.formatter import ReviewReport, ReviewIssue, Severity
    
    issues = []
    lines = code.split('\n')
    
    # Security checks
    security_patterns = {
        'password': 'Hardcoded password detected',
        'secret': 'Hardcoded secret detected',
        'api_key': 'Hardcoded API key detected',
        'token': 'Hardcoded token detected',
        'eval(': 'Dangerous eval() usage',
        'exec(': 'Dangerous exec() usage',
        'os.system': 'Potential command injection',
        'pickle.load': 'Unsafe deserialization'
    }
    
    for i, line in enumerate(lines, 1):
        line_lower = line.lower()
        
        # Security checks
        for pattern, message in security_patterns.items():
            if pattern in line_lower and '=' in line:
                issues.append(ReviewIssue(
                    title=message,
                    description=f"Line {i}: {message}",
                    severity=Severity.HIGH,
                    line_number=i,
                    suggestion="Use environment variables for sensitive data",
                    category="security"
                ))
                break
        
        # Style checks
        if len(line) > 100:
            issues.append(ReviewIssue(
                title="Line Too Long",
                description=f"Line {i} has {len(line)} characters (max 100)",
                severity=Severity.LOW,
                line_number=i,
                suggestion="Break this line into multiple lines for readability",
                category="readability"
            ))
        
        # Naming convention checks
        if 'def ' in line:
            func_name = line.split('def ')[1].split('(')[0].strip() if 'def ' in line else ''
            if func_name and not func_name.islower() and '_' not in func_name:
                if any(c.isupper() for c in func_name[1:]):
                    issues.append(ReviewIssue(
                        title="Naming Convention Issue",
                        description=f"Function '{func_name}' uses camelCase instead of snake_case",
                        severity=Severity.LOW,
                        line_number=i,
                        suggestion=f"Rename to '{_to_snake_case(func_name)}'",
                        category="style"
                    ))
        
        # Missing docstring check
        if 'def ' in line and i + 1 < len(lines):
            next_line = lines[i].strip() if i < len(lines) else ""
            if not ('"""' in next_line or "'''" in next_line):
                func_name = line.split('def ')[1].split('(')[0].strip()
                issues.append(ReviewIssue(
                    title="Missing Docstring",
                    description=f"Function '{func_name}' lacks a docstring",
                    severity=Severity.MEDIUM,
                    line_number=i,
                    suggestion="Add a docstring explaining what the function does",
                    category="best_practices"
                ))
        
        # TODO/FIXME detection
        if 'TODO' in line or 'FIXME' in line:
            issues.append(ReviewIssue(
                title="Unresolved TODO/FIXME",
                description=f"Line {i} contains unresolved comment",
                severity=Severity.MEDIUM,
                line_number=i,
                suggestion="Address this TODO/FIXME before production",
                category="general"
            ))
    
    # If no issues found, add positive feedback
    if not issues:
        issues.append(ReviewIssue(
            title="Code Looks Good! ✅",
            description="No obvious issues detected in this code",
            severity=Severity.LOW,
            line_number=None,
            suggestion="Consider adding unit tests and documentation",
            category="general"
        ))
    
    # Calculate score based on issues
    high_count = sum(1 for i in issues if i.severity == Severity.HIGH)
    medium_count = sum(1 for i in issues if i.severity == Severity.MEDIUM)
    score = max(1, 10 - (high_count * 3) - (medium_count * 1))
    
    report = ReviewReport(
        issues=issues,
        summary=f"Static analysis found {len(issues)} issue(s). Review type: {review_type}",
        overall_score=min(10, score)
    )
    
    return {"report": report, "demo_mode": True}


def _to_snake_case(name: str) -> str:
    """Convert camelCase to snake_case."""
    result = []
    for i, char in enumerate(name):
        if char.isupper() and i > 0:
            result.append('_')
        result.append(char.lower())
    return ''.join(result)


def render_results(result: dict):
    """Render the review results."""
    if not result:
        return
    
    report = result.get("report")
    if not report:
        return
    
    if result.get("demo_mode"):
        st.info("🔔 Running in demo mode (no API key). Results are basic static analysis.")
    
    # Score display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{report.overall_score}/10</div>
            <div class="stat-label">Overall Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        high = sum(1 for i in report.issues if i.severity.name == "HIGH")
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color: #fc8181;">{high}</div>
            <div class="stat-label">High Issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        medium = sum(1 for i in report.issues if i.severity.name == "MEDIUM")
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color: #f6ad55;">{medium}</div>
            <div class="stat-label">Medium Issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        low = sum(1 for i in report.issues if i.severity.name == "LOW")
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color: #48bb78;">{low}</div>
            <div class="stat-label">Low Issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Issues display
    st.markdown("### 📋 Issues Found")
    
    for i, issue in enumerate(report.issues, 1):
        severity_class = f"severity-{issue.severity.name.lower()}"
        with st.expander(f"{issue.severity.value} - {issue.title}", expanded=i <= 3):
            st.markdown(f"**Category:** {issue.category}")
            if issue.line_number:
                st.markdown(f"**Line:** {issue.line_number}")
            st.markdown(f"**Description:** {issue.description}")
            st.markdown(f"**Suggestion:** {issue.suggestion}")
            if issue.improved_code:
                st.markdown("**Improved Code:**")
                st.code(issue.improved_code, language="python")
    
    # Download button
    from utils.formatter import ReviewFormatter
    download_text = ReviewFormatter.format_for_download(report)
    st.download_button(
        label="📥 Download Report",
        data=download_text,
        file_name="code_review_report.txt",
        mime="text/plain"
    )


def main():
    """Main application entry point."""
    init_session_state()
    render_header()
    
    # Sidebar configuration
    settings = render_sidebar()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        code = render_code_input()
        
        if st.button("🚀 Review Code", use_container_width=True):
            result = perform_review(code, settings)
            if result:
                st.session_state.current_review = result
                st.session_state.review_history.append(result)
    
    with col2:
        st.markdown("### 📊 Review Results")
        if st.session_state.current_review:
            render_results(st.session_state.current_review)
        else:
            st.info("Submit code for review to see results here.")


if __name__ == "__main__":
    main()
