import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime # Added missing import

from niku.groq_client import get_groq_completion
from niku.tts_client import text_to_speech
from niku.memory_manager import ConversationHistory
from niku.decision_engine import DecisionEngine # Uncommented
from niku.tools import fetch_weather_data # Added import for weather tool

# Load environment variables from .env file
load_dotenv()

async def main_loop():
    """
    Main loop for the Niku AI assistant.
    """
    print("Niku AI Assistant")
    print("Type 'quit' to exit.")

    # Initialize components
    # Ensure 'logs' directory exists for conversation history
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    conversation_log_path = os.path.join(log_dir, 'niku_chat_history.json')
    history_manager = ConversationHistory(log_file=conversation_log_path, max_history_len=10)

    try:
        decision_engine = DecisionEngine() # Uncommented and initialized
    except ValueError as e:
        print(f"Error initializing Decision Engine: {e}")
        print("Please ensure COHERE_API_KEY is set in your .env file.")
        return

    # --- Get API Keys ---
    groq_api_key = os.getenv("GROQ_API_KEY")
    cohere_api_key = os.getenv("COHERE_API_KEY") # For decision engine

    if not groq_api_key:
        print("Error: GROQ_API_KEY not found in environment variables. Please set it in a .env file.")
        return
    if not cohere_api_key: # Uncommented check
        print("Error: COHERE_API_KEY not found in environment variables. Please set it in a .env file.")
        print("The Decision Engine may not function correctly.")
        # Depending on how critical the decision engine is, you might choose to return here.
        # For now, we'll allow it to proceed but the classify_intent might fail if the key was needed at init.
        # The DecisionEngine class already raises ValueError if key is missing at init.

    print("\\n--- Conversation History Loaded ---")
    for msg in history_manager.get_history():
        print(f"{msg['role'].capitalize()}: {msg['content']}")
    print("-----------------------------------\\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == 'quit':
            print("Niku: Goodbye!")
            break

        if not user_input:
            continue

        history_manager.add_message("user", user_input)

        # --- Intent Classification ---
        print("\\nNiku (Decision Engine): Classifying intent...")
        intent = decision_engine.classify_intent(user_input)
        effective_intent_for_prompt = intent if intent and intent != "unknown_intent" else "general_chat"

        if intent:
            print(f"Niku (Decision Engine): Detected intent - {intent}")
            history_manager.add_message("system", f"Detected user intent: {intent}") # Log intent
        else:
            print("Niku (Decision Engine): Could not determine intent or error occurred.")
            history_manager.add_message("system", "Intent classification failed.") # Log failure

        assistant_response = ""
        # --- Tool Usage or LLM Response ---
        if effective_intent_for_prompt == "get_weather":
            print("\\\\nNiku (LLM for Tool Parameter Extraction): Determining location for weather tool...")
            
            # Define the tool and its required parameters for the LLM
            tool_description_for_llm = {
                "tool_name": "fetch_weather_data",
                "description": "Fetches the current weather for a specified location.",
                "parameters": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, or city and country for which to get the weather (e.g., 'San Francisco, CA', 'London, UK')."
                    }
                }
            }
            
            # Construct a more specific prompt for parameter extraction
            parameter_extraction_prompt = (
                f"You need to determine the parameter for a tool based on the user's query.\\n"
                f"Tool Name: {tool_description_for_llm['tool_name']}\\n"
                f"Tool Description: {tool_description_for_llm['description']}\\n"
                f"Parameter to Extract: 'location' ({tool_description_for_llm['parameters']['location']['description']})\\n\\n"
                f"User Query: '{user_input}'\\n\\n"
                f"Based on the user query, what is the value for the 'location' parameter? "
                f"Respond with only the location name. If no specific location is clearly mentioned or inferable, respond with the exact word 'None'."
            )
            
            extracted_location_raw = get_groq_completion(prompt=parameter_extraction_prompt)
            extracted_location = extracted_location_raw.strip()
            
            history_manager.add_message("system", f"LLM (param_extraction) for 'fetch_weather_data' on query '{user_input}' -> extracted location: '{extracted_location}'")

            if extracted_location and extracted_location.lower() != "none":
                print(f"Niku (Tool): Using weather tool for '{extracted_location}'...")
                assistant_response = fetch_weather_data(extracted_location) 
                history_manager.add_message("system", f"Tool used: fetch_weather_data, input: {extracted_location}")
            else:
                assistant_response = "I can get the weather for you, but I need to know the city. Could you please tell me which city you're interested in?"
                history_manager.add_message("system", "Weather tool skipped: No location identified by LLM for parameter extraction.")
        else:
            # --- Construct a prompt for Groq using recent history and intent ---
            recent_history_messages = history_manager.get_history()[-5:] # Get last 5 messages (includes current user input)
            
            # Modify the latest user message in the history copy based on intent for the prompt
            # This modification is only for the prompt, not for the stored history.
            prompt_specific_messages = [msg.copy() for msg in recent_history_messages] # Create a deep copy for modification

            if prompt_specific_messages and prompt_specific_messages[-1]["role"] == "user":
                last_user_message_content = prompt_specific_messages[-1]["content"]
                if effective_intent_for_prompt == "tell_joke":
                    prompt_specific_messages[-1]["content"] = f"Tell a joke related to: {last_user_message_content}"
                # Add more intent-specific prompt modifications here

            conversation_str_prompt = "\\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in prompt_specific_messages])
            
            # Optional: Add a system message based on intent at the beginning of the prompt string
            system_prompt_prefix = ""
            if effective_intent_for_prompt == "tell_joke":
                system_prompt_prefix = "System: You are an AI that specializes in telling jokes. "
            # ... add other system prefixes based on intent
            
            final_prompt_to_llm = f"{system_prompt_prefix}{conversation_str_prompt}"

            print("\\nNiku is thinking...")
            # print(f"DEBUG: Sending to LLM: {final_prompt_to_llm}") # For debugging the prompt
            llm_response = get_groq_completion(prompt=final_prompt_to_llm)
            if "Error:" in llm_response:
                print(f"Niku (Error): {llm_response}")
                history_manager.add_message("system", f"Error obtaining response from Groq: {llm_response}")
                continue # Skip to next iteration if LLM fails
            assistant_response = llm_response

        print(f"Niku: {assistant_response}")
        history_manager.add_message("assistant", assistant_response)

        # Generate speech for the assistant's response
        # Ensure 'audio_responses' directory exists
        audio_dir = os.path.join(os.path.dirname(__file__), 'audio_responses')
        os.makedirs(audio_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_audio_file = os.path.join(audio_dir, f"niku_response_{timestamp}.mp3")
        
        print(f"Niku (Audio): Generating speech...")
        audio_path = await text_to_speech(assistant_response, output_file=output_audio_file)

        if "Error" not in audio_path:
            print(f"Niku (Audio): Speech saved to: {audio_path}")
            # Here you could add a command to play the audio if a player is available
            # e.g., os.system(f"xdg-open {audio_path}") # For Linux
            # e.g., os.system(f"start {audio_path}") # For Windows
            # e.g., os.system(f"afplay {audio_path}") # For macOS
        else:
            print(f"Niku (Audio Error): {audio_path}")

        print("-----------------------------------\\n")


if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\\nNiku: Exiting due to user interruption.")
    finally:
        print("Niku session ended.")
