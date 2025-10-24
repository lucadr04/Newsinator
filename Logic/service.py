# Logic/news_service.py
from typing import List, Dict, Any
from datetime import datetime
from .fetcher import NewsFetcher
from .summarizer import AISummarizer
from .downloader import DocumentGenerator

class NewsService:
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.ai_summarizer = AISummarizer()
        self.downloader = DocumentGenerator()

        self.available_categories = [
            "Politics",
            "Economy",
            "Technology",
            "Science",
            "Health",
            "Sports"
        ]

        self.available_locations = [
            "Italy",
            "USA",
            "France",
            "Germany",
            "Spain",
            "England",
            "World"
        ]

        self.available_date_ranges = [
            "yesterday",
            "today", # Today only works with a PRO sub to the API
            "this week"
        ]

    def fetch_articles(self, location: str, date_range: str, categories: List[str]) -> List[Dict[str, Any]]:
        """ Fetch articles using the news fetcher """
        return self.news_fetcher.fetch_articles(location, date_range, categories)

    def generate_ai_summary(self, articles: List[Dict[str, Any]]) -> str:
        """ Generate AI summary using the AI summarizer """
        return self.ai_summarizer.generate_summary(articles, focused=True)

    def save_summary_markdown(self, content: str, location: str, categories: List[str]) -> str:
        """Save summary as markdown"""
        filename = self._generate_filename(location, categories, "md")
        return self.downloader.save_markdown(content, filename)

    def save_summary_pdf(self, content: str, location: str, categories: List[str]) -> str:
        """Save summary as PDF"""
        filename = self._generate_filename(location, categories, "pdf")
        return self.downloader.save_as_pdf(content, filename)

    def validate_categories(self, categories: List[str]) -> bool:
        """ Validates that at least one category is selected """
        return len(categories) > 0

    def _generate_filename(self, location: str, categories: List[str], ext: str) -> str:
        """Generate filename"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        topics = "_".join(sorted(categories))
        safe_name = f"NewsReport_{location}_{topics}_{timestamp}.{ext}"
        return "".join(c for c in safe_name if c.isalnum() or c in "._-")