# Logic/news_fetcher.py
import logging
from typing import List, Dict, Any
from newsapi import NewsApiClient
from datetime import datetime, timedelta
from .fetcher_localizer import NewsStrategies  # Import the new class

from config import FETCHER_KEY

class NewsFetcher:
    def __init__(self):
        self.newsapi = None
        self.strategies = None

        if FETCHER_KEY:
            try:
                self.newsapi = NewsApiClient(api_key=FETCHER_KEY)
                self.strategies = NewsStrategies(self.newsapi)
            except:
                pass

    def fetch_articles(self, location: str, date_range: str, categories: List[str]) -> List[Dict[str, Any]]:
        """Main fetching function"""
        if self.strategies:
            articles = self._fetch_real_articles(location, date_range, categories)
            if articles:
                return articles

        return []

    def _fetch_real_articles(self, location: str, date_range: str, categories: List[str]) -> List[Dict[str, Any]]:
        """Fetch real articles by location chosen"""
        try:
            location_methods = {
                "Italy": self.strategies.fetch_italian,
                "France": self.strategies.fetch_french,
                "Germany": self.strategies.fetch_german,
                "England": self.strategies.fetch_english,
                "Spain": self.strategies.fetch_spanish,
                "USA": self.strategies.fetch_usa
            }

            fetch_method = location_methods.get(location, self.strategies.fetch_world)
            return fetch_method(date_range, categories)

        except Exception as e:
            logging.error(f"NewsAPI error: {e}")
            return []