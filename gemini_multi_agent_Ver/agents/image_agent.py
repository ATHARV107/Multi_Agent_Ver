# File: agents/image_agent.py (UPDATED)
import logging
from PIL import Image
import io
import os # Added for os.path.exists check
from core.api_handler import GeminiAPIHandler
from config import VISION_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImageAgent:
    """
    Agent responsible for analyzing image inputs using a vision-capable Gemini model.
    """
    def __init__(self, api_handler: GeminiAPIHandler):
        """
        Initializes the ImageAgent.

        Args:
            api_handler (GeminiAPIHandler): An instance of the Gemini API handler.
        """
        self.api_handler = api_handler
        logging.info("ImageAgent initialized.")

    def analyze_image_from_bytes(self, image_data: bytes, user_prompt: str = None) -> str:
        """
        Analyzes image data (bytes) and answers questions related to it.

        Args:
            image_data (bytes): The raw image data.
            user_prompt (str): An optional text prompt/question related to the image.

        Returns:
            str: A textual analysis or answer related to the image.
        Raises:
            Exception: If image processing or API call fails.
        """
        try:
            # Construct the prompt for the vision model
            vision_prompt = "Analyze this image."
            if user_prompt:
                vision_prompt = f"{vision_prompt} Specifically, {user_prompt}"

            logging.info(f"Sending image to Gemini Vision model '{VISION_MODEL}' with prompt: '{vision_prompt}'")
            response_text = self.api_handler.generate_vision_response(
                model_name=VISION_MODEL,
                image_data=image_data,
                prompt=vision_prompt
            )
            logging.info("Image analysis complete.")
            return response_text
        except Exception as e:
            logging.error(f"Error during image analysis: {e}")
            raise

    # Removed analyze_image method that took a path, as we're now handling bytes directly from Flask upload.
    # If you still need path-based analysis for other purposes, you can keep it or re-add it.

