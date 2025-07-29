# File: core/api_handler.py
import google.generativeai as genai
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GeminiAPIHandler:
    """
    Handles interactions with the Gemini API, including error handling and retries.
    """
    def __init__(self, api_key: str):
        """
        Initializes the Gemini API handler.

        Args:
            api_key (str): Your Gemini API key.
        """
        genai.configure(api_key=api_key)
        self.api_key = api_key

    def _call_gemini_model(self, model_name: str, contents: list, stream: bool = False, safety_settings: list = None, **kwargs): # ADD safety_settings
        """
        Internal method to call a Gemini model with retry logic.

        Args:
            model_name (str): The name of the Gemini model to use (e.g., "gemini-1.5-flash").
            contents (list): The content to send to the model (text, image parts).
            stream (bool): Whether to stream the response.
            safety_settings (list): Optional list of safety settings to apply. # NEW ARG
            **kwargs: Additional arguments for generate_content (e.g., generation_config).

        Returns:
            google.generativeai.types.GenerateContentResponse: The response from the Gemini API.
        Raises:
            Exception: If the API call fails after retries.
        """
        model = genai.GenerativeModel(model_name=model_name)
        retries = 3
        delay = 2  # seconds

        for i in range(retries):
            try:
                logging.info(f"Calling Gemini model '{model_name}' (Attempt {i+1}/{retries})...")
                # Pass safety_settings to generate_content
                response = model.generate_content(contents, stream=stream, safety_settings=safety_settings, **kwargs)
                return response
            except genai.types.BlockedPromptException as e:
                logging.error(f"Prompt blocked by safety settings: {e}")
                raise # Re-raise BlockedPromptException to be handled by GuardrailAgent
            except Exception as e:
                logging.warning(f"API call failed: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
        raise Exception(f"Failed to call Gemini API after {retries} attempts.")

    def generate_text(self, model_name: str, prompt: str, history: list = None, safety_settings: list = None, **kwargs): # ADD safety_settings
        """
        Generates text using a specified Gemini model.

        Args:
            model_name (str): The name of the text model.
            prompt (str): The text prompt.
            history (list): Optional list of previous chat messages for context.
            safety_settings (list): Optional list of safety settings to apply. # NEW ARG
            **kwargs: Additional arguments for generate_content.

        Returns:
            str: The generated text.
        """
        contents = []
        if history:
            for item in history:
                contents.append({'role': item['role'], 'parts': [{'text': item['content']}]})
        contents.append({'role': 'user', 'parts': [{'text': prompt}]})

        response = self._call_gemini_model(model_name, contents, safety_settings=safety_settings, **kwargs) # Pass safety_settings
        return response.text

    def generate_vision_response(self, model_name: str, image_data: bytes, prompt: str = None, safety_settings: list = None, **kwargs): # ADD safety_settings
        """
        Generates a response from a vision-capable Gemini model with an image and optional text.

        Args:
            model_name (str): The name of the vision model (e.g., "gemini-1.5-flash").
            image_data (bytes): The raw image data.
            prompt (str): Optional text prompt to accompany the image.
            safety_settings (list): Optional list of safety settings to apply. # NEW ARG
            **kwargs: Additional arguments for generate_content.

        Returns:
            str: The generated text response.
        """
        # Create a GenerativeModel instance for the vision model
        model = genai.GenerativeModel(model_name=model_name)

        # Prepare content for the vision model
        image_part = {'mime_type': 'image/jpeg', 'data': image_data} # Assuming JPEG, adjust if needed

        contents = [image_part]
        if prompt:
            contents.append({'text': prompt})

        response = self._call_gemini_model(model_name, contents, safety_settings=safety_settings, **kwargs) # Pass safety_settings
        return response.text

