# File: main.py
import os
import sys
import logging
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image # Used for checking image validity, not direct processing in Flask

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import GEMINI_API_KEY, HISTORY_FILE
from core.api_handler import GeminiAPIHandler
from core.context_manager import ContextManager
from agents.guardrail_agent import GuardrailAgent # NEW IMPORT
from agents.image_agent import ImageAgent
from agents.text_agent import TextAgent
from agents.response_agent import ResponseAgent
from agents.action_agent import ActionAgent

# Configure logging for Flask and agents
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder='static')

# Initialize core components and agents globally for the Flask app
api_handler = GeminiAPIHandler(api_key=GEMINI_API_KEY)
context_manager = ContextManager(history_file=HISTORY_FILE)
guardrail_agent = GuardrailAgent(api_handler=api_handler) # NEW AGENT INITIALIZATION
image_agent = ImageAgent(api_handler=api_handler)
text_agent = TextAgent(api_handler=api_handler)
response_agent = ResponseAgent(api_handler=api_handler)
action_agent = ActionAgent()

# Allowed image extensions for upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Checks if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serves the main HTML page."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handles chat requests, supporting both text and image inputs.
    """
    user_input_text = request.form.get('text_input', '').strip()
    uploaded_file = request.files.get('image_file')

    llm_history = context_manager.get_context_for_llm()
    context_summary = ""
    gemini_response = ""
    action_message = ""
    
    # --- GUARDRAIL STEP 1: Input Validation ---
    is_input_safe = True
    guardrail_message = ""

    if uploaded_file and allowed_file(uploaded_file.filename):
        image_data = uploaded_file.read()
        is_input_safe, guardrail_message = guardrail_agent.scan_image_input(image_data, user_prompt=user_input_text)
        # Reset stream position after reading for potential re-reading by agents if needed,
        # though in this flow, image_data is passed directly.
        uploaded_file.seek(0)
    elif user_input_text:
        is_input_safe, guardrail_message = guardrail_agent.scan_text_input(user_input_text)
    else:
        return jsonify({"error": "No text or image input provided."}), 400

    if not is_input_safe:
        # Input was blocked by guardrails
        logging.warning(f"Input blocked by guardrail: {guardrail_message}")
        context_manager.add_message("user", user_input_text if user_input_text else f"[Image: {uploaded_file.filename}]")
        context_manager.add_message("model", f"[Guardrail]: {guardrail_message}")
        return jsonify({"response": f"System: {guardrail_message}", "history": context_manager.get_full_history()})


    try:
        if uploaded_file and allowed_file(uploaded_file.filename):
            # Process image input (only if safe)
            logging.info(f"Received image file: {uploaded_file.filename}")
            # Re-read image data if it was consumed by guardrail_agent.scan_image_input
            # For simplicity, we read once and pass the bytes. If the guardrail agent
            # consumed the stream, you'd need to re-read or pass the bytes.
            # Here, image_data already holds the bytes.
            
            image_analysis = image_agent.analyze_image_from_bytes(image_data, user_prompt=user_input_text)
            context_summary = f"Image analysis: {image_analysis}"

            context_manager.add_message("user", f"[Image: {secure_filename(uploaded_file.filename)}] {user_input_text if user_input_text else 'Image provided.'}")
            context_manager.add_message("model", f"[Image Analysis]: {image_analysis}")
            gemini_response = f"[Image Analysis]: {image_analysis}"

        elif user_input_text:
            # Process text input (only if safe)
            logging.info(f"Received text input: '{user_input_text}'")
            text_analysis = text_agent.analyze_text(user_input_text, history=llm_history)
            context_summary = f"Text analysis: {text_analysis}"

            context_manager.add_message("user", user_input_text)
            context_manager.add_message("model", f"[Text Analysis]: {text_analysis}")
            gemini_response = f"[Text Analysis]: {text_analysis}"

        # Determine if an action is needed based on the combined context
        action_data = action_agent.determine_action(context_summary)
        
        # --- GUARDRAIL STEP 2: Action Validation ---
        is_action_valid, action_validation_message = action_agent.validate_action(action_data)

        if not is_action_valid:
            # Action was blocked by guardrails
            logging.warning(f"Action blocked by guardrail: {action_validation_message}")
            action_message = f"[ACTION BLOCKED]: {action_validation_message}"
        elif action_data["action"] != "none":
            # Action is valid and needs to be executed
            action_agent.execute_action(action_data)
            action_message = f"[ACTION]: {action_data['action']} performed."
            if 'query' in action_data:
                action_message += f" (Query: '{action_data['query']}')"
            elif 'details' in action_data:
                action_message += f" (Details: '{action_data['details'][:50]}...')"
            logging.info(action_message)
        else:
            action_message = "[ACTION]: No specific action determined."
            logging.info(action_message)

        # Generate final response to the user
        final_response_text = response_agent.generate_response(context_summary, history=llm_history)
        context_manager.add_message("model", final_response_text)

        # Combine messages for the UI
        full_response = f"{gemini_response}\n\n{action_message}\n\nGemini: {final_response_text}"

        return jsonify({"response": full_response, "history": context_manager.get_full_history()})

    except Exception as e:
        logging.exception("An error occurred during chat processing.")
        return jsonify({"error": str(e)}), 500

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clears the conversation history."""
    try:
        context_manager.clear_history()
        return jsonify({"message": "History cleared successfully."})
    except Exception as e:
        logging.exception("Error clearing history.")
        return jsonify({"error": str(e)}), 500

@app.route('/get_history', methods=['GET'])
def get_history():
    """Returns the current conversation history."""
    return jsonify({"history": context_manager.get_full_history()})

if __name__ == '__main__':
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    
    app.run(debug=True)

