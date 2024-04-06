import json

from openai import OpenAI
import os
import random


class Chatbot:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.threads = {}
        self.active_thread = None

    @staticmethod
    def chat_with_gpt(conversation_history):
        prompt = "\n".join(conversation_history)
        openai = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].message.content

    def save_conversation(self, thread_id):
        conversation_history = self.threads[thread_id]
        filename = f"conversations/conversation_history_{thread_id}.txt"
        print(thread_id)
        self.save_conversation_to_file(conversation_history, filename)

    def load_conversation(self, thread_id):
        filename = f"conversations/conversation_history_{thread_id}.txt"
        conversation_history = self.load_conversation_from_file(filename)
        if conversation_history is None:
            conversation_history = []
        self.threads[thread_id] = conversation_history
        return conversation_history

    @staticmethod
    def load_conversation_from_file(filename):
        if not os.path.exists(filename):
            directory = os.path.dirname(filename)
            if not os.path.exists(directory):
                os.makedirs(directory)
            open(filename, 'w').close()  # Crea el archivo vacío si no existe
            return []

        with open(filename, 'r') as file:
            content = file.read()
            if not content:
                return []
            return [line.strip() for line in content.splitlines()]

    @staticmethod
    def save_conversation_to_file(conversation_history, filename):
        with open(filename, 'w') as file:
            for message in conversation_history:
                file.write(message + '\n')

    def create_thread(self):
        thread_id = str(len(self.threads) + 1)
        self.threads[thread_id] = []
        self.active_thread = thread_id
        self.save_threads()
        return thread_id

    def save_threads(self):
        threads_directory = 'threads'
        if not os.path.exists(threads_directory):
            os.makedirs(threads_directory)

        threads_file = os.path.join(threads_directory, 'threads.json')
        with open(threads_file, 'w') as file:
            json.dump(self.threads, file)

    def switch_thread(self, thread_id):
        if thread_id in self.threads:
            self.active_thread = thread_id
            self.load_conversation(thread_id)
        else:
            print(f"Thread {thread_id} does not exist.")

    def load_threads(self):
        threads_directory = 'threads'
        threads_file = os.path.join(threads_directory, 'threads.json')

        try:
            with open(threads_file, 'r') as file:
                self.threads = json.load(file)
        except FileNotFoundError:
            self.threads = {}

    def run(self):
        print("Welcome to the Chatbot! Type 'quit' to exit.")
        self.create_thread()

        while True:
            user_input = input("You: ")
            if user_input.lower() == 'q':
                break
            elif user_input.lower() == 'new thread':
                thread_id = self.create_thread()
                print(f"Created new thread with ID: {thread_id}")
            elif user_input.lower().startswith('switch thread'):
                thread_id = user_input.split()[-1]
                self.switch_thread(thread_id)
            else:
                conversation_history = self.threads[self.active_thread]
                conversation_history.append(user_input)
                self.save_conversation(self.active_thread)
                response = Chatbot.chat_with_gpt(conversation_history)
                conversation_history.append(response)


if __name__ == "__main__":
    chatbot = Chatbot(api_key='openai_api_key')
    chatbot.run()
