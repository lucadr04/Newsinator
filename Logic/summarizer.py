import logging
from typing import List, Dict, Any
from config import SUMMARIZER_KEY
from .article_processor import ArticleProcessor
from .prompt_manager import ChainManager

try:
    from langchain_google_genai import ChatGoogleGenerativeAI

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class AISummarizer:
    """AI summarizer without mock fallbacks"""

    def __init__(self):
        self.api_key = SUMMARIZER_KEY
        self.llm = None
        self.chain_manager = None
        self.article_processor = ArticleProcessor()
        self._init_llm()

    def _init_llm(self):
        """Initialize AI components"""
        if not LANGCHAIN_AVAILABLE or not self.api_key:
            return

        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-lite",
                google_api_key=self.api_key,
                temperature=0.7,
                max_tokens=2000
            )
            self.chain_manager = ChainManager(self.llm)
        except Exception as e:
            logging.error(f"AI initialization failed: {e}")

    def generate_summary(self, articles: List[Dict[str, Any]], focused: bool = True) -> str:
        """Generate summary or return error"""
        selected = [a for a in articles if a.get('selected', False)]
        if not selected:
            return "## Error\nPlease select articles to summarize."

        if not all([LANGCHAIN_AVAILABLE, self.api_key, self.chain_manager]):
            return self._get_config_error()

        try:
            cores = self.article_processor.extract_article_cores_advanced(selected)
            if not cores:
                return "## Error\nNo meaningful content in selected articles."

            docs = self.article_processor.prepare_documents_from_cores(selected, cores)
            chain = self.chain_manager.focused_chain if focused else self.chain_manager.standard_chain
            summary = chain.invoke({"context": docs})

            return self._format_output(selected, summary, focused)

        except Exception as e:
            logging.error(f"Summarization error: {e}")
            return f"## Error\nAI summarization failed: {str(e)}"

    def _get_config_error(self) -> str:
        """Get configuration error message"""
        if not LANGCHAIN_AVAILABLE:
            return "## Error\nInstall: pip install langchain langchain-google-genai"
        if not self.api_key:
            return "## Error\nSet SUMMARIZER_KEY in config.py"
        return "## Error\nAI service unavailable"

    def _format_output(self, articles: List[Dict], summary: str, focused: bool) -> str:
        """Format the summary output"""
        sources = list(set(a.get('source', 'Unknown') for a in articles))
        header = "## News Brief\n\n" if focused else "## Comprehensive Analysis\n\n"

        return f"""{header}{summary}

**Sources**: {', '.join(sources[:3])}
**Articles**: {len(articles)}

### Sources
{self._format_article_list(articles)}
"""

    def _format_article_list(self, articles: List[Dict]) -> str:
        """Format article list"""
        return "\n".join(
            f"- [{a.get('title', 'Untitled')}]({a.get('url')}) ({a.get('source', 'Unknown')})"
            for a in articles[:10]
        )