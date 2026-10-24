
import requests

API_URL = "http://127.0.0.1:8000/ai/chat"

messages = [
    "Berapa jumlah seluruh tugas operasional saya? Rincikan jumlah tugas berdasarkan status.",
    "Tampilkan tugas yang belum selesai beserta ID, judul, dan statusnya.",
    "Apakah ada kemungkinan tugas duplikat? Sebutkan ID dan alasannya, tetapi jangan menghapus apa pun.",
    "Bantu saya menentukan urutan prioritas tugas berdasarkan data yang tersedia. Jelaskan jika prioritasnya hanya perkiraan."
]

for i, message in enumerate(messages, start=1):
    print(f"\n{'=' * 50}")
    print(f"PERTANYAAN {i}")
    print(f"{'=' * 50}")
    print(message)

    try:
        response = requests.post(
            API_URL,
            json={"message": message},
            timeout=120
        )

        if response.ok:
            result = response.json()

            print("\nJAWABAN AI:")
            print(result["reply"])

            if "data_summary" in result:
                print("\nRINGKASAN DATA:")
                print(result["data_summary"])
        else:
            print(f"\nRequest gagal: HTTP {response.status_code}")
            print(response.text)

    except requests.RequestException as error:
        print(f"\nRequest gagal: {error}")

    except (ValueError, KeyError) as error:
        print(f"\nRespons tidak dapat dibaca: {error}")
