// File: static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('text-input');
    const imageUpload = document.getElementById('image-upload');
    const fileNameSpan = document.getElementById('file-name');
    const sendButton = document.getElementById('send-button');
    const clearButton = document.getElementById('clear-button');
    const chatHistoryDiv = document.getElementById('chat-history');
    const loadingIndicator = document.getElementById('loading-indicator');

    let currentImageFile = null;

    // --- Utility Functions ---

    /**
     * Displays a message in the chat history.
     * @param {string} sender - 'user' or 'gemini'.
     * @param {string} message - The text message to display.
     * @param {string} [imageUrl=null] - Optional URL for an image to display.
     */
    function displayMessage(sender, message, imageUrl = null) {
        const messageBubble = document.createElement('div');
        messageBubble.classList.add('message-bubble', 'flex', 'flex-col');

        if (sender === 'user') {
            messageBubble.classList.add('user-bubble', 'self-end');
        } else {
            messageBubble.classList.add('gemini-bubble', 'self-start');
        }

        if (imageUrl) {
            const imgElement = document.createElement('img');
            imgElement.src = imageUrl;
            imgElement.classList.add('max-w-full', 'h-auto', 'rounded-lg', 'mb-2');
            imgElement.onerror = () => { imgElement.src = 'https://placehold.co/150x100/CCCCCC/000000?text=Image+Load+Error'; }; // Fallback
            messageBubble.appendChild(imgElement);
        }

        const textElement = document.createElement('p');
        // Replace newline characters with <br> for proper display in HTML
        textElement.innerHTML = message.replace(/\n/g, '<br>');
        messageBubble.appendChild(textElement);

        chatHistoryDiv.appendChild(messageBubble);
        chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight; // Scroll to bottom
    }

    /**
     * Toggles the visibility of the loading indicator.
     * @param {boolean} show - True to show, false to hide.
     */
    function toggleLoading(show) {
        if (show) {
            loadingIndicator.classList.remove('hidden');
            sendButton.disabled = true;
            clearButton.disabled = true;
            textInput.disabled = true;
            imageUpload.disabled = true;
        } else {
            loadingIndicator.classList.add('hidden');
            sendButton.disabled = false;
            clearButton.disabled = false;
            textInput.disabled = false;
            imageUpload.disabled = false;
        }
    }

    /**
     * Fetches and displays the initial conversation history from the backend.
     */
    async function loadHistory() {
        try {
            const response = await fetch('/get_history');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            chatHistoryDiv.innerHTML = ''; // Clear existing history
            data.history.forEach(item => {
                // For simplicity, we assume image content in history is just text analysis.
                // If you want to display the original image, you'd need to store its URL/data in history.json
                // and handle it here. For now, we only display text content.
                displayMessage(item.role, item.content);
            });
        } catch (error) {
            console.error('Error loading history:', error);
            displayMessage('gemini', 'Error loading chat history.');
        }
    }

    // --- Event Listeners ---

    imageUpload.addEventListener('change', (event) => {
        currentImageFile = event.target.files[0];
        if (currentImageFile) {
            fileNameSpan.textContent = currentImageFile.name;
        } else {
            fileNameSpan.textContent = 'No file chosen';
        }
    });

    sendButton.addEventListener('click', async () => {
        const text = textInput.value.trim();
        const image = currentImageFile;

        if (!text && !image) {
            alert('Please enter some text or select an image.');
            return;
        }

        toggleLoading(true);

        // Display user's input immediately
        if (text) {
            displayMessage('user', text);
        }
        if (image) {
            const imageUrl = URL.createObjectURL(image);
            displayMessage('user', `Image: ${image.name}`, imageUrl);
        }

        const formData = new FormData();
        if (text) {
            formData.append('text_input', text);
        }
        if (image) {
            formData.append('image_file', image);
        }

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            displayMessage('gemini', data.response); // Display Gemini's full response

            // Clear inputs after sending
            textInput.value = '';
            imageUpload.value = ''; // Clear file input
            fileNameSpan.textContent = 'No file chosen';
            currentImageFile = null;

        } catch (error) {
            console.error('Error sending message:', error);
            displayMessage('gemini', `Sorry, an error occurred: ${error.message}`);
        } finally {
            toggleLoading(false);
        }
    });

    clearButton.addEventListener('click', async () => {
        toggleLoading(true);
        try {
            const response = await fetch('/clear_history', {
                method: 'POST',
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            chatHistoryDiv.innerHTML = ''; // Clear UI history
            displayMessage('gemini', 'Conversation history cleared!');
        } catch (error) {
            console.error('Error clearing history:', error);
            displayMessage('gemini', `Sorry, an error occurred while clearing history: ${error.message}`);
        } finally {
            toggleLoading(false);
        }
    });

    // Load history when the page loads
    loadHistory();
});

// File: static/script.js
console.log("script.js is attempting to load!"); // <--- ADD THIS LINE
document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('text-input');
    // ... rest of your code
});