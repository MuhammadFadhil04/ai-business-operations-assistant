
import os
from dotenv import load_dotenv
from google import genai

# Membaca konfigurasi dari file .env
load_dotenv()

# Mengambil API key tanpa menampilkannya
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY tidak ditemukan di file .env")
    raise SystemExit(1)

try:
    # Membuat client Gemini
    client = genai.Client(api_key=api_key)

    print("Menghubungi Gemini API...")

    # Mengirim pertanyaan sederhana ke AI
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Jelaskan fungsi AI untuk membantu operasional bisnis dalam 2 kalimat."
    )

    print("\nJawaban Gemini:")
    print(response.text)

    print("\nBERHASIL: Gemini API dapat digunakan.")

except Exception as error:
    print("\nGAGAL: Permintaan ke Gemini API tidak berhasil.")
    print("Jenis error:", type(error).__name__)
    print("Detail:", str(error))
