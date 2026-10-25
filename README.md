# AI Business Operations Assistant

Aplikasi lokal untuk mengelola tugas operasional melalui antarmuka web dan AI Chat Agent. Backend menyediakan REST API dengan FastAPI, menyimpan tugas di SQLite, dan dapat mengirim event tugas ke n8n.

## Teknologi

- Python 3.10+
- FastAPI dan Uvicorn
- SQLite
- Google Gemini API (`google-genai`)
- Frontend HTML, CSS, dan JavaScript tanpa langkah build
- n8n sebagai integrasi webhook opsional

## Fitur

- Membuat, melihat, mengubah, dan menghapus tugas.
- Mengelola status, deadline, dan tingkat kepentingan.
- Mengurutkan tugas berdasarkan prioritas, deadline, atau waktu pembuatan.
- Memberi rekomendasi prioritas dari skor deadline dan kepentingan.
- Menangani perintah tugas terstruktur dan konfirmasi penghapusan melalui AI Chat Agent.
- Mengirim event tugas ke n8n jika webhook dikonfigurasi.

## Persiapan

Jalankan dari PowerShell pada Windows:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Isi `.env` secara lokal. Jangan commit atau membagikan file itu. Template `.env.example` hanya berisi nama variabel tanpa kredensial.

## Konfigurasi

Atur variabel berikut di `.env`:

| Variabel | Kegunaan |
| --- | --- |
| `GEMINI_API_KEY` | Kunci API untuk AI Chat Agent. Diperlukan agar chat dapat memakai Gemini. |
| `N8N_WEBHOOK_URL` | URL webhook n8n. Opsional. |
| `N8N_WEBHOOK_SECRET` | Secret yang dikirim pada header `X-API-Key` ke n8n. Opsional; isi bersama URL webhook. |

Tanpa konfigurasi n8n, operasi CRUD tetap berjalan. Event tidak dikirim.

## Menjalankan aplikasi

Buka dua terminal PowerShell dari folder project.

Terminal pertama menjalankan backend:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

Terminal kedua menyajikan frontend:

```powershell
python -m http.server 5500 --directory frontend
```

Buka `http://127.0.0.1:5500`. Dokumentasi interaktif API tersedia di `http://127.0.0.1:8000/docs`.

## Database

SQLite menyimpan data pada `business.db` di folder project. File ini tetap ada setelah proses backend dimulai ulang dan diabaikan oleh Git. Buat salinan cadangan secara privat jika data perlu dipindahkan atau dipulihkan.

## Pengujian

Jalankan pengujian backend dan perintah AI yang tidak memerlukan layanan eksternal:

```powershell
$env:PYTHON_DOTENV_DISABLED = "1"
python -m pytest -q test_backend.py test_ai_commands.py
```

Pengujian tersebut menggunakan mock untuk error Gemini dan kegagalan n8n, sehingga tidak mengirim permintaan ke layanan eksternal. `test_gemini_connection.py` adalah pemeriksaan manual yang benar-benar menghubungi Gemini; jalankan hanya jika memang ingin menguji koneksi langsung.

## Catatan keamanan

Aplikasi ini ditujukan untuk penggunaan lokal. API belum memiliki autentikasi; endpoint DELETE dapat menghapus tugas langsung, sementara perintah penghapusan dari AI Chat Agent meminta konfirmasi token. Jangan membuka API ke jaringan publik tanpa menambahkan autentikasi dan otorisasi.
