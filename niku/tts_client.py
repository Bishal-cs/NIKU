\
import asyncio
import edge_tts
import os

async def text_to_speech(text: str, voice: str = "en-US-AriaNeural", output_file: str = "response.mp3") -> str:
    """
    Converts text to speech using Edge TTS and saves it to an audio file.

    Args:
        text: The text to convert to speech.
        voice: The voice to use for speech synthesis.
        output_file: The path to save the audio file.

    Returns:
        The path to the saved audio file, or an error message.
    """
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        return os.path.abspath(output_file)
    except Exception as e:
        return f"Error during text-to-speech conversion: {e}"

async def main():
    # Example usage
    text_to_speak = "Hello, this is Niku speaking. I hope you are having a wonderful day!"
    print(f"Converting text to speech: '{text_to_speak}'")
    output_path = await text_to_speech(text_to_speak)

    if "Error" not in output_path:
        print(f"Speech saved to: {output_path}")
        # You can add code here to play the audio file if you have a player installed
        # For example, on Linux, you might use:
        # os.system(f"xdg-open {output_path}")
    else:
        print(output_path)

if __name__ == "__main__":
    # Ensure the script is run in a directory where it can write the output file
    # Or provide an absolute path for output_file
    # For example, to save in the current script's directory:
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # output_file_path = os.path.join(script_dir, "response.mp3")
    # asyncio.run(text_to_speech(text_to_speak, output_file=output_file_path))
    asyncio.run(main())
