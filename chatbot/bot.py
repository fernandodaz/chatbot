import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


class Chatbot:
    """
    A class to manage chatbot interactions and conversations.

    Attributes:
        api_key (str): The API key for the OpenAI API.
        threads (dict): A dictionary to store conversation threads.
        active_thread (str): The ID of the currently active conversation thread.
    """

    def __init__(self, api_key=None):
        """
        Initialize the Chatbot with an optional API key.

        Args:
            api_key (str, optional): The API key for the OpenAI API. Defaults to None.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.threads = {}
        self.active_thread = None

    @staticmethod
    def chat_with_gpt(conversation_history):
        """
        Send a conversation history to the GPT model and return its response.

        Args:
            conversation_history (list): A list of messages in the conversation.

        Returns:
            str: The response from the GPT model.
        """
        prompt = "\n".join(conversation_history)
        openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
        """
        Save the conversation history of a thread to a file.

        Args:
            thread_id (str): The ID of the thread to save.
        """
        conversation_history = self.threads[thread_id]
        filename = f"conversations/conversation_history_{thread_id}.txt"
        self.save_conversation_to_file(conversation_history, filename)

    def load_conversation(self, thread_id):
        """
        Load the conversation history of a thread from a file.

        Args:
            thread_id (str): The ID of the thread to load.

        Returns:
            list: The conversation history of the thread.
        """
        filename = f"conversations/conversation_history_{thread_id}.txt"
        conversation_history = self.load_conversation_from_file(filename)
        if conversation_history is None:
            conversation_history = []
        self.threads[thread_id] = conversation_history
        return conversation_history

    @staticmethod
    def load_conversation_from_file(filename):
        """
        Load a conversation history from a file.

        Args:
            filename (str): The name of the file to load from.

        Returns:
            list: The conversation history loaded from the file.
        """
        if not os.path.exists(filename):
            directory = os.path.dirname(filename)
            if not os.path.exists(directory):
                os.makedirs(directory)
            open(filename, 'w', encoding='utf-8').close()  # Create an empty file if it doesn't exist
            return []

        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
                if not content:
                    return []
                return [line.strip() for line in content.splitlines()]
        except Exception as e:
            print(f"Error loading conversation from file: {e}")
            return []

    @staticmethod
    def save_conversation_to_file(conversation_history, filename):
        """
        Save a conversation history to a file.

        Args:
            conversation_history (list): The conversation history to save.
            filename (str): The name of the file to save to.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                for message in conversation_history:
                    file.write(message + '\n')
        except Exception as e:
            print(f"Error saving conversation to file: {e}")

    def create_thread(self):
        """
        Create a new conversation thread.

        Returns:
            str: The ID of the newly created thread.
        """
        thread_id = str(len(self.threads) + 1)
        self.threads[thread_id] = []
        self.active_thread = thread_id
        self.save_threads()
        return thread_id

    def save_threads(self):
        """
        Save the list of threads to a file.
        """
        threads_directory = 'threads'
        if not os.path.exists(threads_directory):
            os.makedirs(threads_directory)

        threads_file = os.path.join(threads_directory, 'threads.json')
        try:
            with open(threads_file, 'w', encoding='utf-8') as file:
                json.dump(self.threads, file)
        except Exception as e:
            print(f"Error saving threads to file: {e}")

    def switch_thread(self, thread_id):
        """
        Switch the active thread to a specified thread ID.

        Args:
            thread_id (str): The ID of the thread to switch to.
        """
        if thread_id in self.threads:
            self.active_thread = thread_id
            self.load_conversation(thread_id)
        else:
            print(f"Thread {thread_id} does not exist.")

    def load_threads(self):
        """
        Load the list of threads from a file.
        """
        threads_directory = 'threads'
        threads_file = os.path.join(threads_directory, 'threads.json')

        try:
            with open(threads_file, 'r', encoding='utf-8') as file:
                self.threads = json.load(file)
        except FileNotFoundError:
            self.threads = {}
        except Exception as e:
            print(f"Error loading threads from file: {e}")

    def run(self):
        """
        Run the chatbot CLI.
        """
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
    chatbot = Chatbot()
    chatbot.run()
