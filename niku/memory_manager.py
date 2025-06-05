import json
import os
from datetime import datetime

DEFAULT_LOG_FILE = 'logs/niku_chat_history.json'

class ConversationHistory:
    """
    Manages the conversation history using a JSON file.
    """
    def __init__(self, log_file: str = DEFAULT_LOG_FILE, max_history_len: int | None = None):
        """
        Initializes the ConversationHistory.

        Args:
            log_file: The path to the JSON file for storing conversation logs.
            max_history_len: Optional. Maximum number of messages to keep in history.
                               If None, all history is kept.
        """
        self.log_file = os.path.abspath(log_file)
        self.max_history_len = max_history_len
        self.history = self._load_history()

    def _load_history(self) -> list[dict]:
        """Loads conversation history from the JSON file."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding= 'utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading history from {self.log_file}: {e}. Starting with empty history.")
                return []
        return []

    def _save_history(self):
        """Saves the current conversation history to the JSON file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving history to {self.log_file}: {e}")

    def add_message(self, role: str, content: str):
        """
        Adds a message to the conversation history.

        Args:
            role: The role of the speaker (e.g., "user", "assistant", "system").
            content: The content of the message.
        """
        if not role or not content:
            print("Error: Role and content cannot be empty.")
            return

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(), # ISO 8601 format
        }
        self.history.append(message)

        if self.max_history_len is not None and len(self.history) > self.max_history_len:
            self.history = self.history[-self.max_history_len:]

        self._save_history()

    def get_history(self) -> list[dict]:
        """
        Retrieves the current conversation history.

        Returns:
            A list of message dictionaries.
        """
        return self.history.copy() # Return a copy to prevent external modification

    def clear_history(self):
        """Clears the conversation history."""
        self.history = []
        self._save_history()
        print(f"Conversation history cleared from {self.log_file}")

if __name__ == "__main__":
    # Example Usage
    # To save logs in a 'logs' subdirectory:
    # log_dir = os.path.join(os.path.dirname(__file__), \'..\', \'logs\') # Assuming niku/logs
    # os.makedirs(log_dir, exist_ok=True)
    # conversation_log_path = os.path.join(log_dir, \'niku_chat_history.json\')
    # memory = ConversationHistory(log_file=conversation_log_path, max_history_len=10)

    # Default usage (saves in the script's directory or CWD if run directly)
    memory = ConversationHistory(log_file= DEFAULT_LOG_FILE, max_history_len=5)

    print(f"Initial history (loaded from {memory.log_file}):")
    for msg in memory.get_history():
        print(f"- [{msg['timestamp']}] {msg['role']}: {msg['content']}")

    print("\\nAdding new messages...")
    memory.add_message("user", "Hello Niku!")
    memory.add_message("assistant", "Hello there! How can I help you today?")
    memory.add_message("user", "Tell me a fun fact.")
    memory.add_message("assistant", "Bees can recognize human faces!")

    print("\\nUpdated history:")
    for msg in memory.get_history():
        print(f"- [{msg['timestamp']}] {msg['role']}: {msg['content']}")

    # Example of exceeding max_history_len
    if memory.max_history_len:
        print(f"\\nAdding more messages to test max_history_len ({memory.max_history_len})...")
        memory.add_message("user", "What is the capital of France?")
        memory.add_message("assistant", "The capital of France is Paris.")
        memory.add_message("user", "And the capital of Japan?")
        memory.add_message("assistant", "That would be Tokyo!")

        print("\\nFinal history (should be truncated if over limit):")
        for msg in memory.get_history():
            print(f"- [{msg['timestamp']}] {msg['role']}: {msg['content']}")

    # memory.clear_history()
    # print("\\nHistory after clearing:")
    # for msg in memory.get_history():
    #     print(f"- [{msg[\'timestamp\']}] {msg[\'role\']}: {msg[\'content\']}")
