from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found. Please add it to your .env file")

client = Groq(api_key=groq_api_key)

# Conversation history with sliding window
# Each entry is a dict with 'role' (user/assistant) and 'content'
conversation_history = []
MAX_HISTORY = 20  # Keep last 20 messages (10 Q&A pairs)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Add user message to conversation history
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Create messages array with system prompt and full conversation history
        messages = [
            {
                "role": "system",
                "content": "You are a helpful and friendly AI assistant. Provide concise, accurate, and engaging responses. Use markdown formatting when appropriate for better readability (e.g., **bold**, *italic*, `code`, lists, etc.)."
            }
        ] + conversation_history
        
        # Call Groq API with full conversation context
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",  
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=False
        )
        
        # Get the assistant's response
        assistant_message = chat_completion.choices[0].message.content
        
        # Add assistant response to conversation history
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Maintain sliding window - remove oldest Q&A pair if exceeds limit
        while len(conversation_history) > MAX_HISTORY:
            # Remove the oldest user-assistant pair (2 messages)
            conversation_history.pop(0)
            if len(conversation_history) > 0:
                conversation_history.pop(0)
        
        print(f"[USER]: {user_message}")
        print(f"[ASSISTANT]: {assistant_message}")
        print(f"[HISTORY LENGTH]: {len(conversation_history)} messages")
        
        return jsonify({
            'response': assistant_message,
            'conversation_length': len(conversation_history)
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_conversation():
    """Clear the conversation history"""
    global conversation_history
    conversation_history = []
    print("[INFO]: Conversation history cleared")
    return jsonify({'message': 'Conversation cleared successfully'})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'conversation_length': len(conversation_history),
        'max_history': MAX_HISTORY
    })

if __name__ == '__main__':
    print("Starting AI Chatbot Backend...")
    print(f"Max conversation history: {MAX_HISTORY} messages")
    app.run(host='0.0.0.0', port=5000, debug=True)