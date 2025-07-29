# File: agents/guardrail_agent.py
import logging
import google.generativeai as genai # Needed for safety settings constants
from core.api_handler import GeminiAPIHandler
from config import TEXT_MODEL, VISION_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GuardrailAgent:
    """
    Agent responsible for applying guardrails to user inputs (text and images).
    It detects, logs, and blocks malicious content.
    """
    def __init__(self, api_handler: GeminiAPIHandler):
        """
        Initializes the GuardrailAgent.

        Args:
            api_handler (GeminiAPIHandler): An instance of the Gemini API handler.
        """
        self.api_handler = api_handler
        logging.info("GuardrailAgent initialized.")

        # Default safety settings for Gemini API calls.
        # BLOCK_NONE means the API will block content only if it's very likely to be unsafe.
        # You can adjust these thresholds as needed: HARM_BLOCK_THRESHOLD_LOW, MEDIUM, HIGH, UNSPECIFIED
        self.default_safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

    def _log_blocked_content(self, input_type: str, content: str, reason: str):
        """Logs details of blocked content."""
        logging.warning(f"GUARDRAIL BLOCKED - Type: {input_type}, Reason: {reason}, Content: '{content[:100]}...'")
        # In a real system, you'd send this to a dedicated logging/monitoring service.

    def scan_text_input(self, text_input: str) -> (bool, str):
        """
        Scans text input for malicious content using Gemini's safety features
        and basic rule-based checks.

        Args:
            text_input (str): The user's text input.

        Returns:
            tuple[bool, str]: (True if safe, False if blocked), and a message.
        """
        # 1. Basic Rule-Based Checks (can be expanded)
        malicious_keywords = ["delete all files", "Hacking","format hard drive", "steal credit card", "harm yourself", "do something illegal"]
        for keyword in malicious_keywords:
            if keyword in text_input.lower():
                self._log_blocked_content("text", text_input, f"Rule-based: detected '{keyword}'")
                return False, "Your request contains content that violates our safety guidelines. Please rephrase your query."

        # 2. Gemini API Safety Check (using a dummy call to trigger safety filters)
        # We make a minimal call just to see if the content is blocked by Gemini's internal filters.
        # This is a bit of a workaround as directly checking input safety isn't a standalone API.
        try:
            # Use a very low temperature to make the model deterministic for this check
            # and a very short max_output_tokens as we don't care about the response, just if it's blocked.
            self.api_handler.generate_text(
                model_name=TEXT_MODEL,
                prompt=text_input,
                safety_settings=self.default_safety_settings,
                generation_config={"temperature": 0.0, "max_output_tokens": 1}
            )
            return True, "Text input is safe."
        except genai.types.BlockedPromptException as e:
            self._log_blocked_content("text", text_input, f"Gemini API blocked: {e}")
            return False, "Your request was blocked by safety filters. Please try a different query."
        except Exception as e:
            logging.error(f"Error during Gemini safety scan for text: {e}")
            # If the safety check itself fails, we might block or allow based on policy
            return False, "An internal error occurred during safety check. Please try again."


    def scan_image_input(self, image_data: bytes, user_prompt: str = None) -> (bool, str):
        """
        Scans image input for malicious content using Gemini's safety features.

        Args:
            image_data (bytes): The raw image data.
            user_prompt (str): Optional text prompt accompanying the image.

        Returns:
            tuple[bool, str]: (True if safe, False if blocked), and a message.
        """
        # Similar to text, use a dummy call to trigger vision model's safety filters
        try:
            vision_prompt = "Is this image safe? Describe any unsafe content if present."
            if user_prompt:
                vision_prompt = f"{vision_prompt} Also consider: {user_prompt}"

            self.api_handler.generate_vision_response(
                model_name=VISION_MODEL,
                image_data=image_data,
                prompt=vision_prompt,
                safety_settings=self.default_safety_settings,
                generation_config={"temperature": 0.0, "max_output_tokens": 1}
            )
            return True, "Image input is safe."
        except genai.types.BlockedPromptException as e:
            self._log_blocked_content("image", f"Image data (bytes) with prompt: {user_prompt}", f"Gemini API blocked: {e}")
            return False, "The image you provided was blocked by safety filters. Please try a different image."
        except Exception as e:
            logging.error(f"Error during Gemini safety scan for image: {e}")
            return False, "An internal error occurred during image safety check. Please try again."

