"""
This module defines the Flask application for the chatbot.
"""

import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from chatbot.bot import Chatbot

# Load environment variables from .env file
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
chatbot = Chatbot(api_key=openai_api_key)


@app.route('/')
def home():
    """
    Render the home page of the chatbot application.

    Returns:
        str: The rendered HTML template for the home page.
    """
    return render_template('index.html')


@app.route('/new_thread', methods=['POST'])
def new_thread():
    """
    Create a new chat thread.

    Returns:
        json: A JSON object containing the thread ID.
    """
    thread_id = chatbot.create_thread()
    return jsonify({'thread_id': thread_id})


@app.route('/threads', methods=['GET'])
def get_threads():
    """
    Load and return all chat threads.

    Returns:
        json: A JSON object containing a list of thread IDs.
    """
    chatbot.load_threads()
    threads = list(chatbot.threads.keys())
    return jsonify({'threads': threads})


@app.route('/load_thread', methods=['POST'])
def load_thread():
    """
    Load a specific chat thread by its ID.

    Returns:
        json: A JSON object containing the conversation history of the thread.
    """
    thread_id = request.form.get('thread_id')
    if thread_id not in chatbot.threads:
        return jsonify({'error': 'Thread not found'}), 404
    conversation_history = chatbot.load_conversation(thread_id)
    return jsonify({'messages': conversation_history})


@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle a chat message from the user.

    Returns:
        json: A JSON object containing the chatbot's response.
    """
    user_input = request.form.get('user_input')
    thread_id = request.form.get('thread_id')
    if user_input.lower() == 'quit':
        return jsonify({'response': 'Goodbye!'})
    conversation_history = chatbot.load_conversation(thread_id)
    conversation_history.append("User: " + user_input)
    chatbot.save_conversation(thread_id)
    response = Chatbot.chat_with_gpt(conversation_history)
    conversation_history.append("Chatbot: " + response)
    chatbot.save_conversation(thread_id)
    return jsonify({'response': response})


if __name__ == "__main__":
    app.run(debug=True)
