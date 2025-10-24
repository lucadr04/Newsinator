import os
from dotenv import load_dotenv

load_dotenv()

FETCHER_KEY = os.getenv("FETCHER_KEY")
SUMMARIZER_KEY = os.getenv("SUMMARIZER_KEY")