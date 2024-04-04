from flask import Flask, request, jsonify, render_template
from chatbot.bot import Chatbot
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
chatbot = Chatbot(api_key=openai_api_key)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/new_thread', methods=['POST'])
def new_thread():
    thread_id = chatbot.create_thread()
    return jsonify({'thread_id': thread_id})


@app.route('/threads', methods=['GET'])
def get_threads():
    chatbot.load_threads()
    threads = list(chatbot.threads.keys())
    return jsonify({'threads': threads})


@app.route('/load_thread', methods=['POST'])
def load_thread():
    thread_id = request.form.get('thread_id')
    if thread_id not in chatbot.threads:
        return jsonify({'error': 'Thread not found'}), 404
    conversation_history = chatbot.load_conversation(thread_id)
    return jsonify({'messages': conversation_history})


@app.route('/chat', methods=['POST'])
def chat():
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
