# File: config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file or environment variables.")

# Define models to use
# gemini-1.5-flash is generally faster and cheaper for many tasks.
# gemini-1.5-pro is more powerful for complex reasoning.
TEXT_MODEL = "gemini-1.5-flash"
VISION_MODEL = "gemini-1.5-flash" # Use a vision-capable model for image inputs

# History file path
HISTORY_FILE = "history.json"

