
import unittest
from main import detect_possible_duplicates


class TestDetectPossibleDuplicates(unittest.TestCase):

    def test_duplicate_tasks_detected(self):
        tasks = [
            {
                "id": 3,
                "title": "Membuat laporan penjualan",
                "description": "Menyiapkan laporan penjualan harian."
            },
            {
                "id": 5,
                "title": "Membuat laporan penjualan",
                "description": "Menyiapkan laporan penjualan harian."
            }
        ]

        result = detect_possible_duplicates(tasks)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["task_ids"], [3, 5])

    def test_different_titles_not_duplicate(self):
        tasks = [
            {"id": 1, "title": "Memeriksa stok", "description": "Cek barang"},
            {"id": 2, "title": "Membuat laporan", "description": "Cek barang"}
        ]

        result = detect_possible_duplicates(tasks)

        self.assertEqual(result, [])

    def test_different_descriptions_not_duplicate(self):
        tasks = [
            {"id": 1, "title": "Membuat laporan", "description": "Laporan harian"},
            {"id": 2, "title": "Membuat laporan", "description": "Laporan bulanan"}
        ]

        result = detect_possible_duplicates(tasks)

        self.assertEqual(result, [])

    def test_case_and_outer_spaces_ignored(self):
        tasks = [
            {"id": 1, "title": " Laporan Penjualan ", "description": "Data Harian"},
            {"id": 2, "title": "laporan penjualan", "description": "data harian"}
        ]

        result = detect_possible_duplicates(tasks)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["task_ids"], [1, 2])

    def test_empty_list(self):
        result = detect_possible_duplicates([])

        self.assertEqual(result, [])

    def test_empty_titles_ignored(self):
        tasks = [
            {"id": 1, "title": "", "description": "Deskripsi A"},
            {"id": 2, "title": "", "description": "Deskripsi A"}
        ]

        result = detect_possible_duplicates(tasks)

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
