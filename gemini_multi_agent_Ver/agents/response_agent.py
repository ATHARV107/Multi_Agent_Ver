import logging
from core.api_handler import GeminiAPIHandler
from config import TEXT_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ResponseAgent:
    """
    Agent responsible for generating user-facing responses based on the current context.
    """
    def __init__(self, api_handler: GeminiAPIHandler):
        """
        Initializes the ResponseAgent.

        Args:
            api_handler (GeminiAPIHandler): An instance of the Gemini API handler.
        """
        self.api_handler = api_handler
        logging.info("ResponseAgent initialized.")

    def generate_response(self, context_summary: str, history: list) -> str:
        """
        Generates a natural language response for the user based on the aggregated context.

        Args:
            context_summary (str): A summary or key insights from the context manager.
            history (list): The full conversation history.

        Returns:
            str: The user-friendly response.
        """
        prompt = f"Based on the following context and conversation history, generate a helpful and concise response to the user. \n\nContext/Analysis: {context_summary}\n\n"
        
        logging.info(f"Generating user response with Gemini model '{TEXT_MODEL}'.")
        user_response = self.api_handler.generate_text(
            model_name=TEXT_MODEL,
            prompt=prompt,
            history=history # Pass history for better context understanding
        )
        logging.info("User response generated.")
        return user_response