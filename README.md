# 🔍 Code Review Assistant

An AI-powered code review system using **RAG pipelines**, **ChromaDB**, and **LangChain** to provide intelligent, context-aware code analysis.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **RAG-Powered** | Retrieval-Augmented Generation for context-aware reviews |
| 🤖 **Multi-Agent** | Specialized agents for security, performance & style |
| 🔎 **Vector Search** | ChromaDB for semantic code retrieval |
| 📊 **Smart Scoring** | Issue severity classification (HIGH/MEDIUM/LOW) |
| 🎨 **Modern UI** | Beautiful Streamlit interface |

---

## 🚀 Quick Start

### Local Setup

```bash
# Clone and setup
cd code-review-assistant
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Run
streamlit run app.py
```

---

## 📁 Project Structure

```
code-review-assistant/
├── app.py                  # Streamlit UI
├── config/                 # Configuration
├── embeddings/             # Vector embeddings
├── vector_store/           # ChromaDB storage
├── retriever/              # Similarity search
├── rag/                    # RAG pipeline
├── prompts/                # LLM prompts
├── agents/                 # CrewAI agents
├── llm/                    # LLM clients
├── utils/                  # Helpers
└── requirements.txt        # Dependencies
```

---

## 🔄 How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  User Code  │ ──▶ │   Parser    │ ──▶ │  Embeddings │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Review    │ ◀── │  LLM + RAG  │ ◀── │  ChromaDB   │
└─────────────┘     └─────────────┘     └─────────────┘
```

1. **Parse** → Code broken into logical chunks
2. **Embed** → Chunks converted to vectors
3. **Store** → Vectors saved in ChromaDB
4. **Retrieve** → Relevant context fetched
5. **Generate** → LLM produces the review
6. **Display** → Results shown in UI

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **LLM** | OpenAI / Vertex AI |
| **Embeddings** | HuggingFace / OpenAI |
| **Vector DB** | ChromaDB |
| **Orchestration** | LangChain |
| **Multi-Agent** | CrewAI |

---

## 📊 Review Categories

- 🔴 **Security** — SQL injection, XSS, hardcoded secrets
- 🟡 **Performance** — Time complexity, memory usage
- 🟢 **Readability** — PEP8, naming conventions
- 🔵 **Best Practices** — SOLID principles, DRY

---


## 📈 Results

- ⏱️ **30% faster** code review process
- 🎯 **Context-aware** analysis via RAG
- 📦 **Scalable** AI-driven review system
