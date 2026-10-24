
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    print("BERHASIL: Gemini API key berhasil dibaca.")
else:
    print("GAGAL: GEMINI_API_KEY belum ditemukan.")
