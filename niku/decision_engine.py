\
import os
import cohere
from dotenv import load_dotenv

load_dotenv()

class DecisionEngine:
    """
    Handles intent classification and decision making using Cohere.
    """
    def __init__(self):
        """
        Initializes the DecisionEngine with the Cohere API key.
        """
        self.cohere_api_key = os.environ.get("COHERE_API_KEY")
        if not self.cohere_api_key:
            raise ValueError("COHERE_API_KEY not found in environment variables. Please set it in a .env file.")
        self.co = cohere.Client(self.cohere_api_key)

    def classify_intent(self, text: str, examples: list[dict] | None = None) -> str | None:
        """
        Classifies the intent of a given text using Cohere's classify endpoint.

        Args:
            text: The input text to classify.
            examples: A list of examples for few-shot classification.
                      Each example should be a dict with "text" and "label" keys.
                      Example: [{"text": "What's the weather like?", "label": "get_weather"},
                                {"text": "Tell me a joke.", "label": "tell_joke"}]

        Returns:
            The predicted intent label (str) or None if classification fails.
        """
        if not examples:
            # Define some default examples if none are provided
            examples = [
                cohere.ClassifyExample(text="What is the weather like today?", label="get_weather"),
                cohere.ClassifyExample(text="Can you tell me a joke?", label="tell_joke"),
                cohere.ClassifyExample(text="What time is it?", label="get_time"),
                cohere.ClassifyExample(text="I want to chat.", label="general_chat"),
                cohere.ClassifyExample(text="Who are you?", label="identity_query"),
            ]

        try:
            response = self.co.classify(
                model='embed-english-v3.0', # Using a default embedding model
                inputs=[text],
                examples=examples
            )
            if response.classifications and response.classifications[0].prediction:
                return response.classifications[0].prediction
            else:
                print(f"Warning: Could not classify intent for text: '{text}'. Response: {response}")
                return "unknown_intent" # Fallback intent
        except cohere.CohereAPIError as e:
            print(f"Cohere API Error during intent classification: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during intent classification: {e}")
            return None

if __name__ == '__main__':
    # Example Usage
    # Ensure COHERE_API_KEY is set in your .env file:
    # COHERE_API_KEY="your_actual_cohere_api_key"

    engine = DecisionEngine()

    queries = [
        "Tell me something funny.",
        "What's the current temperature in London?",
        "Hello, how are you doing?",
        "Who built you?"
    ]

    # Example custom examples (optional, can be tailored to specific use cases)
    custom_examples = [
        cohere.ClassifyExample(text="I'd like to hear a funny story.", label="tell_joke"),
        cohere.ClassifyExample(text="What's the forecast for tomorrow?", label="get_weather"),
        cohere.ClassifyExample(text="Just wanted to talk.", label="general_chat"),
        cohere.ClassifyExample(text="What is your name?", label="identity_query"),
        cohere.ClassifyExample(text="Can you help me with my homework?", label="assistance_request"),
    ]

    print("Classifying with default examples:")
    for query in queries:
        intent = engine.classify_intent(query)
        print(f"Query: '{query}' -> Intent: {intent}")

    print("\\nClassifying with custom examples:")
    for query in queries:
        intent = engine.classify_intent(query, examples=custom_examples)
        print(f"Query: '{query}' -> Intent: {intent}")

    # Example of a query that might not fit well
    unknown_query = "The sky is blue and the grass is green."
    print(f"\\nClassifying an ambiguous query: '{unknown_query}'")
    intent = engine.classify_intent(unknown_query, examples=custom_examples)
    print(f"Query: '{unknown_query}' -> Intent: {intent}")
