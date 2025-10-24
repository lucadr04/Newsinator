# AI News Summarizer

Desktop app that fetches and summarizes news using AI. Built with PySide6 and Google Gemini.

## Features

- Fetch news from multiple sources
- AI summaries with Google Gemini  
- Select articles to analyze
- Export as Markdown or PDF
- Filter by location and categories

## Setup

```bash
# Install
pip install PySide6 langchain-google-genai newsapi-python python-dotenv

# Create .env file
echo "FETCHER_KEY=your_newsapi_key_here" > .env
echo "SUMMARIZER_KEY=your_gemini_key_here" >> .env

# Run
python main.py