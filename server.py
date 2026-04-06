import os
import base64
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from elevenlabs.client import ElevenLabs

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Clients ──
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
elevenlabs    = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

chat = gemini_client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=(
            "Your name is VISION, and you are an AI assistant that helps users "
            "with their questions. You are highly intelligent, helpful, "
            "professional, and very friendly."
        ),
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        max_output_tokens=300,
    ),
)

VOICE_ID = "ErXwobaYiN019PkySvjV"


class ChatRequest(BaseModel):
    message: str
    tts: bool = True 


@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # 1. Get Gemini reply
    response = chat.send_message(req.message)
    reply = response.text.strip()

    audio_b64 = None
    if req.tts and reply:
        try:
            audio_bytes = b"".join(
                elevenlabs.text_to_speech.convert(
                    text=reply,
                    voice_id=VOICE_ID,
                    model_id="eleven_flash_v2_5",
                    output_format="mp3_44100_128",
                )
            )
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        except Exception as e:
            print(f"[ElevenLabs error] {e}")

    return {"response": reply, "audio": audio_b64}


@app.get("/")
async def root():
    return {"status": "V.I.S.I.O.N online"}