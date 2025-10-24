# News Summarizer

Desktop GUI app that fetches and summarizes news.

## Features

- Fetch news from multiple sources using [NewsAPI](https://newsapi.org)
- AI summaries with [Google Gemini](aistudio.google.com)
- Filter by location and categories
- Select articles to analyze
- Export as Markdown or PDF
- Graphical interface made with [PySide6](pypi.org/project/PySide6/)

## Setup

```bash
# Install
pip install PySide6 langchain-google-genai newsapi-python python-dotenv

# Create .env file
echo "FETCHER_KEY=your_newsapi_key_here" > .env
echo "SUMMARIZER_KEY=your_gemini_key_here" >> .env

# Run
python main.py
