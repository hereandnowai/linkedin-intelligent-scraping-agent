"""Configuration settings for LinkedIn CTO Scraping Agent."""
import os
from dotenv import load_dotenv

load_dotenv()

# LinkedIn Settings
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")

# OpenAI Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Rate Limiting
MIN_DELAY_SECONDS = int(os.getenv("MIN_DELAY_SECONDS", "3"))
MAX_DELAY_SECONDS = int(os.getenv("MAX_DELAY_SECONDS", "7"))
MAX_PROFILES_PER_SESSION = int(os.getenv("MAX_PROFILES_PER_SESSION", "50"))

# Data Fields to Extract
PROFILE_FIELDS = [
    "name",
    "headline",
    "location",
    "current_company",
    "current_position",
    "experience",
    "education",
    "skills",
    "about",
    "profile_url"
]

# Search Settings
SEARCH_KEYWORDS = ["CTO", "Chief Technology Officer"]

# Browser Settings
HEADLESS = False  # Set to True to run browser in headless mode
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Paths
COOKIES_DIR = "cookies"
DATA_DIR = "data"
LOGS_DIR = "logs"

# Create directories if they don't exist
for directory in [COOKIES_DIR, DATA_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)
