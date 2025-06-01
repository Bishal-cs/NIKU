\
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def get_groq_completion(prompt: str, model: str = "llama3-70b-8192") -> str:
    """
    Gets a completion from the Groq API.

    Args:
        prompt: The prompt to send to the language model. This can be a single string
                or a formatted conversation history.
        model: The model to use for completion.

    Returns:
        The model's response.
    """
    try:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return "Error: GROQ_API_KEY not found in environment variables. Please set it in a .env file."

        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user", # For simplicity, we'll pass the whole prompt as a user message.
                                  # For better results, structure with system/user/assistant turns if prompt is conversational.
                    "content": prompt, 
                }
            ],
            model=model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error interacting with Groq API: {e}"

if __name__ == '__main__':
    # Example usage (requires GROQ_API_KEY to be set in .env)
    # Create a .env file in the root directory with:
    # GROQ_API_KEY="your_actual_api_key"
    
    # Example of a conversational prompt string
    # conversation_prompt = """
    # System: You are Niku, a helpful AI.
    # User: Hello!
    # Assistant: Hi there! How can I help you today?
    # User: Tell me about large language models.
    # """
    # response = get_groq_completion(conversation_prompt)
    
    response = get_groq_completion("Explain the importance of large language models in AI development.")
    print(response)
