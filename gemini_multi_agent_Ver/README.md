Gemini Multi-Agent Chat with Guardrails
This project implements a multi-agentic architecture capable of processing both text and image inputs, generating appropriate responses, and taking actions, all while maintaining conversation context and incorporating robust guardrails for safety. The system leverages the Google Gemini API for its core AI capabilities and provides a simple web-based user interface using Flask.

Features
Multi-Modal Input: Supports both text and image inputs from the user.

Multi-Agent Architecture:

Guardrail Agent: Filters malicious inputs (text and image) and validates proposed actions.

Text Agent: Processes and analyzes text-based queries.

Image Agent: Analyzes images and answers related questions.

Response Agent: Crafts user-friendly natural language responses.

Action Agent: Determines and "executes" system actions based on context (currently placeholders).

Context Management: Maintains conversation history for long-turn interactions.

Safety Guardrails (Assignment 2 Implementation):

Input Moderation: Utilizes Gemini's built-in safety features and rule-based checks to block harmful text and images.

Action Validation: Prevents agents from attempting to perform potentially illegal or unauthorized actions.

Web UI: A simple, interactive web interface for easy interaction.

Getting Started
Follow these steps to set up and run the project on your local machine.

Prerequisites
Python 3.9+: Download and install from python.org.

Visual Studio Code (VS Code): Recommended IDE, download from code.visualstudio.com.

VS Code Python Extension: Install it from the VS Code Extensions Marketplace.

1. Obtain Your Gemini API Key
Go to Google AI Studio.

Sign in with your Google account.

Navigate to "Get API key" or "API key" and click "Create API key in new project" (or "Create API key").

Copy your generated API key. Keep it secure!

2. Project Setup
Clone the Repository (or download the project files):

git clone <your-github-repo-link>
cd gemini_multi_agent

(Replace <your-github-repo-link> with the actual link to your public GitHub repository after you've pushed the code.)

Create a Virtual Environment:
It's best practice to use a virtual environment to manage project dependencies.

python -m venv .venv

Activate the Virtual Environment:

On Windows (PowerShell):

.venv\Scripts\Activate.ps1

On macOS/Linux (Bash/Zsh):

source .venv/bin/activate

You should see (.venv) at the beginning of your terminal prompt.

Install Dependencies:

pip install Flask google-generativeai python-dotenv Pillow

Set Your Gemini API Key:

In the root of your gemini_multi_agent directory, create a new file named .env.

Add the following line to the .env file, replacing "YOUR_GEMINI_API_KEY_HERE" with the API key you obtained in Step 1:

GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"

Important: The .env file is included in .gitignore to prevent your API key from being accidentally pushed to your public repository.

3. Run the Application
Ensure your virtual environment is active.

Start the Flask server:

python main.py

You will see output indicating that the Flask app is running, typically on http://127.0.0.1:5000.

4. Interact with the UI
Open your web browser and navigate to the address provided by Flask (e.g., http://127.0.0.1:5000).

Send Text Messages: Type your query into the text area and click "Send".

Send Images: Click "Upload Image", select an image file, and optionally type a question related to the image in the text area before clicking "Send".

Clear History: Use the "Clear History" button to reset the conversation.

Architecture Overview
The system is designed with a modular, multi-agent approach to handle different aspects of the user interaction:

main.py (Flask App): The central entry point, serving the web UI and routing requests to the appropriate agents.

core/api_handler.py: Manages all direct interactions with the Google Gemini API, including retry logic and passing safety settings.

core/context_manager.py: Handles the persistence and retrieval of conversation history, maintaining context for multi-turn interactions.

agents/guardrail_agent.py:

Input Guardrail: The first line of defense, scanning both text and image inputs for harmful content using Gemini's built-in safety features and custom keywords.

Action Guardrail: Validates proposed actions from the ActionAgent to prevent unauthorized or illegal operations.

agents/text_agent.py: Processes and analyzes text inputs that pass the guardrails, extracting intent or summarizing content.

agents/image_agent.py: Analyzes image inputs (along with optional text prompts) using Gemini's vision capabilities to answer questions related to the image.

agents/response_agent.py: Synthesizes information from various agents and the context to generate a coherent, user-facing natural language response.

agents/action_agent.py: Determines if specific system actions (like web searches or data saving) are required based on the conversation, and "executes" them (currently as placeholders).

Known Limitations and Future Improvements
Placeholder Actions: The ActionAgent currently only prints messages to the console for actions like "web search" or "save data."

Future Improvement: Integrate with real external APIs (e.g., Google Search API, a database, a calendar API) to perform actual actions.

Basic Rule-Based Guardrails: The rule-based checks in GuardrailAgent are simple keyword matching.

Future Improvement: Enhance with more sophisticated NLP techniques, sentiment analysis, or fine-tuned models for more nuanced detection of malicious intent.

Image History Display: The UI currently only displays text analysis for images in the history, not the original image.

Future Improvement: Implement a mechanism to store and retrieve image URLs or base64 data to display original images in the chat history.

Scalability: The current Flask setup is for development.

Future Improvement: Deploy using a production-ready WSGI server (e.g., Gunicorn, uWSGI) and potentially containerize with Docker for better scalability and deployment.

User Authentication: The system currently doesn't have user authentication.

Future Improvement: Implement user login/registration and personalize conversations or manage user-specific data.

Error Handling: While basic error handling is present, more granular error messages and recovery strategies could be implemented.