import logging
from core.api_handler import GeminiAPIHandler
from config import TEXT_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TextAgent:
    """
    Agent responsible for analyzing text inputs using a text-focused Gemini model.
    """
    def __init__(self, api_handler: GeminiAPIHandler):
        """
        Initializes the TextAgent.

        Args:
            api_handler (GeminiAPIHandler): An instance of the Gemini API handler.
        """
        self.api_handler = api_handler
        logging.info("TextAgent initialized.")

    def analyze_text(self, text_input: str, history: list) -> str:
        """
        Analyzes a given text input, potentially extracting intent or summarizing.

        Args:
            text_input (str): The raw text input from the user.
            history (list): The conversation history for context.

        Returns:
            str: A processed or analyzed version of the text input.
        """
        # The text agent can perform various NLP tasks.
        # For simplicity, it will just echo the text and ask for clarification or provide a summary.
        # In a real app, this could involve intent recognition, entity extraction, etc.

        prompt = f"The user said: '{text_input}'. Based on the conversation history, what is the main intent or key information in this statement? Keep it concise for internal processing."
        
        logging.info(f"Analyzing text with Gemini model '{TEXT_MODEL}' for intent/summary.")
        analysis_response = self.api_handler.generate_text(
            model_name=TEXT_MODEL,
            prompt=prompt,
            history=history # Pass history for better context understanding
        )
        logging.info("Text analysis complete.")
        return analysis_response