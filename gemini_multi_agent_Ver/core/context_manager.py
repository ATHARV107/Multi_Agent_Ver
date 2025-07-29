# File: core/context_manager.py
import json
import logging
import os
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ContextManager:
    """
    Manages the conversation history and context for the multi-agent system.
    Handles loading, saving, and updating the conversation state.
    """
    def __init__(self, history_file: str = "history.json", max_history_turns: int = 10):
        """
        Initializes the ContextManager.

        Args:
            history_file (str): Path to the JSON file for persistent history.
            max_history_turns (int): Maximum number of turns to keep in memory for context.
        """
        self.history_file = history_file
        self.max_history_turns = max_history_turns
        self.conversation_history: List[Dict[str, Any]] = self._load_history()
        logging.info(f"ContextManager initialized. Loaded {len(self.conversation_history)} turns from {history_file}.")

    def _load_history(self) -> List[Dict[str, Any]]:
        """
        Loads conversation history from the specified JSON file.
        """
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    # Ensure history is a list of dictionaries with 'role' and 'content'
                    if isinstance(history, list) and all(isinstance(item, dict) and 'role' in item and 'content' in item for item in history):
                        return history
                    else:
                        logging.warning(f"Invalid history format in {self.history_file}. Starting with empty history.")
                        return []
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from {self.history_file}: {e}. Starting with empty history.")
                return []
            except Exception as e:
                logging.error(f"Error loading history from {self.history_file}: {e}. Starting with empty history.")
                return []
        return []

    def _save_history(self):
        """
        Saves the current conversation history to the JSON file.
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=4)
            logging.info(f"Conversation history saved to {self.history_file}.")
        except Exception as e:
            logging.error(f"Error saving history to {self.history_file}: {e}")

    def add_message(self, role: str, content: Any):
        """
        Adds a new message to the conversation history.

        Args:
            role (str): The role of the speaker ("user" or "model").
            content (Any): The content of the message (text, or a representation of image analysis).
        """
        self.conversation_history.append({'role': role, 'content': content})
        # Keep only the most recent turns to manage context length
        if len(self.conversation_history) > self.max_history_turns:
            self.conversation_history = self.conversation_history[-self.max_history_turns:]
        self._save_history()
        logging.info(f"Added message to history (role: {role}). Current history length: {len(self.conversation_history)}")

    def get_full_history(self) -> List[Dict[str, Any]]:
        """
        Returns the full conversation history.
        """
        return self.conversation_history

    def clear_history(self):
        """
        Clears the entire conversation history.
        """
        self.conversation_history = []
        self._save_history()
        logging.info("Conversation history cleared.")

    def get_context_for_llm(self) -> List[Dict[str, str]]:
        """
        Prepares a simplified history format suitable for LLM context.
        This method returns a list of dictionaries, each with 'role' and 'content' keys,
        which is the format expected by api_handler.py's generate_text method for its 'history' argument.
        """
        llm_context = []
        for turn in self.conversation_history:
            # Only include text content for the LLM context.
            # The api_handler.py's generate_text will convert this into the 'parts' format.
            if isinstance(turn['content'], str):
                llm_context.append({'role': turn['role'], 'content': turn['content']}) # Corrected: return 'content' directly
        return llm_context
