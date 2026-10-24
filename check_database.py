
from database import get_connection

connection = get_connection()

tables = connection.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print("Tabel yang ditemukan:")
for table in tables:
    print("-", table["name"])

connection.close()
