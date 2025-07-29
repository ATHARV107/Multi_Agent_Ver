# File: agents/action_agent.py
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ActionAgent:
    """
    Agent responsible for determining and executing appropriate system actions.
    This includes guardrails to prevent illegal actions.
    """
    def __init__(self):
        logging.info("ActionAgent initialized.")

    def _log_blocked_action(self, action_type: str, details: Any, reason: str):
        """Logs details of blocked actions."""
        logging.error(f"ACTION BLOCKED - Type: {action_type}, Reason: {reason}, Details: {details}")
        # In a real system, this would trigger alerts or more severe logging.

    def validate_action(self, action_data: Dict[str, Any]) -> (bool, str):
        """
        Validates a proposed action to ensure it's not illegal or harmful.

        Args:
            action_data (Dict[str, Any]): The action dictionary (e.g., {'action': 'web_search', 'query': '...'}).

        Returns:
            tuple[bool, str]: (True if valid, False if blocked), and a message.
        """
        action_type = action_data.get("action")
        details = action_data.get("query") or action_data.get("data") or action_data.get("details")

        # --- Action-Specific Guardrails (Examples - customize based on your needs) ---
        if action_type == "web_search":
            if details and any(keyword in details.lower() for keyword in ["illegal drugs", "violent acts", "child exploitation", "harmful chemicals"]):
                self._log_blocked_action(action_type, details, "Illegal content search detected.")
                return False, "Cannot perform web search for harmful or illegal content."
            if "delete" in details.lower() or "format" in details.lower():
                 self._log_blocked_action(action_type, details, "Potentially destructive search query.")
                 return False, "Cannot perform web search for potentially destructive actions."

        elif action_type == "save_data":
            if details and any(keyword in details.lower() for keyword in ["credit card numbers", "ssn", "passwords of others"]):
                self._log_blocked_action(action_type, details, "Attempt to save sensitive data.")
                return False, "Cannot save highly sensitive personal information."
            # Add more checks, e.g., if data is too large, or attempts to overwrite critical system files
            
        elif action_type == "schedule_meeting":
            if details and any(keyword in details.lower() for keyword in ["bomb threat", "illegal gathering"]):
                self._log_blocked_action(action_type, details, "Attempt to schedule illegal activity.")
                return False, "Cannot schedule meetings related to illegal activities."

        # Prevent any unknown or potentially dangerous actions
        if action_type not in ["none", "web_search", "save_data", "schedule_meeting"]:
            self._log_blocked_action(action_type, details, "Attempted unknown or unauthorized action type.")
            return False, f"Unsupported or unauthorized action: '{action_type}'."

        return True, "Action is valid."

    def determine_action(self, context_summary: str) -> Dict[str, Any]:
        """
        Determines if a specific action needs to be taken based on the context.
        This is where you'd integrate with external APIs, databases, etc.

        Args:
            context_summary (str): A summary or key insights from the context manager.

        Returns:
            Dict[str, Any]: A dictionary indicating the action to take and any relevant parameters.
                            Returns {'action': 'none'} if no action is needed.
        """
        logging.info(f"ActionAgent analyzing context for potential actions: {context_summary[:100]}...")

        # --- Placeholder Logic (from Assignment 1) ---
        # In a real application, you would use an LLM with function calling
        # or rule-based logic to determine actions based on `context_summary`.

        if "search the web for" in context_summary.lower():
            query = context_summary.lower().split("search the web for", 1)[1].strip()
            logging.info(f"Action: Web search requested for '{query}'")
            return {"action": "web_search", "query": query}
        elif "save this information" in context_summary.lower():
            logging.info("Action: Save information requested.")
            return {"action": "save_data", "data": context_summary}
        elif "schedule" in context_summary.lower() and "meeting" in context_summary.lower():
            logging.info("Action: Meeting scheduling requested.")
            return {"action": "schedule_meeting", "details": context_summary}
        else:
            logging.info("Action: No specific action determined.")
            return {"action": "none"}

    def execute_action(self, action_data: Dict[str, Any]):
        """
        Executes the determined action. This method is called ONLY after
        the action has been validated by `validate_action`.

        Args:
            action_data (Dict[str, Any]): The action dictionary returned by determine_action.
        """
        action_type = action_data.get("action")
        if action_type == "web_search":
            query = action_data.get("query")
            print(f"\n[ACTION]: Performing web search for: '{query}' (Placeholder: In a real app, this would use a search API like Google Search).")
        elif action_type == "save_data":
            data = action_data.get("data")
            print(f"\n[ACTION]: Saving data: '{data[:50]}...' (Placeholder: In a real app, this would save to a database or file).")
        elif action_type == "schedule_meeting":
            details = action_data.get("details")
            print(f"\n[ACTION]: Scheduling meeting with details: '{details[:50]}...' (Placeholder: In a real app, this would integrate with a calendar API).")
        elif action_type == "none":
            pass # No action needed
        else:
            logging.warning(f"Unknown action type: {action_type} passed to execute_action. This should have been caught by validate_action.")

