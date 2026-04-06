import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from RealtimeSTT import AudioToTextRecorder
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
from elevenlabs import stream

MAX_OUTPUT_TOKENS = 50

def main():
    load_dotenv()

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

    if not gemini_api_key:
        raise ValueError("Error: GEMINI_API_KEY not found. Please set it in your .env file.")

    if not elevenlabs_api_key:
        raise ValueError("Error: ELEVENLABS_API_KEY not found. Please set it in your .env file.")

    print("API KEY IS FINEEEE")

    client = genai.Client(api_key=gemini_api_key)
    elevenlabs = ElevenLabs(
        api_key=elevenlabs_api_key,
        )

    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="Your name is VISION, and you are an AI assistant that helps users with their questions. You are highly intelligent, helpful, professional, and very friendly.",
            thinking_config=types.ThinkingConfig(thinking_budget = 0),
            max_output_tokens=MAX_OUTPUT_TOKENS
        ),
    )

    recorder = AudioToTextRecorder(model="tiny.en", language = "en", spinner = False)

    while True:
        print("You: ", end = "", flush=True)
        user_input = recorder.text()
        print(user_input)
        if user_input.lower() == "exit":
            break

        response = chat.send_message_stream(user_input)
        full_response = []

        for chunk in response:
            print(chunk.text, end="", flush=True)
            full_response.append(chunk.text)

        full_response_text = "".join(full_response).strip()
        print()

        if full_response_text:
            audio_stream = elevenlabs.text_to_speech.stream(
                text = full_response_text,
                voice_id = "ErXwobaYiN019PkySvjV",
                model_id = "eleven_flash_v2_5",
                output_format = "mp3_44100_128"
            )
            play(audio_stream)
            
    recorder.shutdown()

if __name__ == "__main__":
    main()