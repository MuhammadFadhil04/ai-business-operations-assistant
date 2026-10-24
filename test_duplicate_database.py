
import crud
from main import detect_possible_duplicates

tasks = crud.get_all_tasks()
duplicates = detect_possible_duplicates(tasks)

print(f"Total tugas di database: {len(tasks)}")
print(f"Jumlah kelompok kemungkinan duplikat: {len(duplicates)}")

if duplicates:
    print("\nTugas yang terindikasi duplikat:")

    for group in duplicates:
        print(f"ID tugas: {group['task_ids']}")
        print(f"Judul: {group['title']}")
        print(f"Deskripsi: {group['description']}")
        print(f"Alasan: {group['reason']}")
        print("-" * 40)
else:
    print("\nTidak ditemukan tugas yang terindikasi duplikat.")
