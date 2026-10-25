
import sqlite3
from pathlib import Path

# Lokasi database berada di folder project.
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "business.db"


def get_connection():
    """Membuka koneksi ke database SQLite."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Membuat tabel dan menambahkan kolom yang diperlukan."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Periksa kolom yang sudah tersedia.
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(tasks)"
            ).fetchall()
        }

        # Migrasi deadline tanpa menghapus data lama.
        if "deadline" not in columns:
            connection.execute(
                "ALTER TABLE tasks ADD COLUMN deadline TEXT"
            )

        # Migrasi tingkat kepentingan.
        # Tugas lama akan memperoleh nilai normal.
        if "importance" not in columns:
            connection.execute(
                """
                ALTER TABLE tasks
                ADD COLUMN importance TEXT NOT NULL DEFAULT 'normal'
                """
            )


if __name__ == "__main__":
    init_db()
    print(f"Database berhasil disiapkan: {DATABASE_PATH}")
