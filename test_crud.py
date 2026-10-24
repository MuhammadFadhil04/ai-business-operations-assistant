
from crud import (
    create_task,
    get_task_by_id,
    update_task,
    delete_task,
)

# CREATE: buat tugas khusus untuk pengujian
task = create_task(
    title="Tugas untuk pengujian CRUD",
    description="Data sementara untuk menguji Update dan Delete.",
)
task_id = task["id"]

print("1. Tugas awal:")
print(get_task_by_id(task_id))

# UPDATE: ubah status dan judul tugas
updated_task = update_task(
    task_id,
    title="Memeriksa stok barang",
    status="completed",
)

print("\n2. Setelah Update:")
print(updated_task)

# DELETE: hapus tugas pengujian
deleted = delete_task(task_id)

print("\n3. Hasil Delete:")
print("Berhasil dihapus:", deleted)

# READ: pastikan tugas sudah tidak ada
remaining_task = get_task_by_id(task_id)

print("\n4. Pemeriksaan akhir:")
print("Data setelah dihapus:", remaining_task)

assert updated_task["title"] == "Memeriksa stok barang"
assert updated_task["status"] == "completed"
assert deleted is True
assert remaining_task is None

print("\nSemua pengujian Update dan Delete berhasil!")
