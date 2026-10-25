
from database import get_connection

UNSET = object()
ALLOWED_IMPORTANCE = {"low", "normal", "high"}


def create_task(
    title,
    description=None,
    deadline=None,
    importance="normal",
):
    """Menambahkan tugas operasional baru."""
    if not title or not title.strip():
        raise ValueError("Judul tugas tidak boleh kosong.")

    if importance not in ALLOWED_IMPORTANCE:
        raise ValueError("Tingkat kepentingan tugas tidak valid.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (
                title, description, deadline, importance
            )
            VALUES (?, ?, ?, ?)
            """,
            (title.strip(), description, deadline, importance),
        )

        task_id = cursor.lastrowid

        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        return dict(row)


def get_all_tasks():
    """Mengambil seluruh tugas operasional."""
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()

        return [dict(row) for row in rows]


def get_task_by_id(task_id):
    """Mengambil satu tugas berdasarkan ID."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        return dict(row) if row else None


def update_task(
    task_id,
    title=None,
    description=None,
    status=None,
    deadline=UNSET,
    importance=UNSET,
):
    """Memperbarui data tugas berdasarkan ID."""
    allowed_statuses = {"pending", "in_progress", "completed"}

    with get_connection() as connection:
        existing_task = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if existing_task is None:
            return None

        new_title = (
            title if title is not None else existing_task["title"]
        )
        new_description = (
            description
            if description is not None
            else existing_task["description"]
        )
        new_status = (
            status if status is not None else existing_task["status"]
        )
        new_deadline = (
            deadline
            if deadline is not UNSET
            else existing_task["deadline"]
        )
        new_importance = (
            importance
            if importance is not UNSET
            else existing_task["importance"]
        )

        if not new_title or not new_title.strip():
            raise ValueError("Judul tugas tidak boleh kosong.")

        if new_status not in allowed_statuses:
            raise ValueError("Status tugas tidak valid.")

        if new_importance not in ALLOWED_IMPORTANCE:
            raise ValueError("Tingkat kepentingan tugas tidak valid.")

        connection.execute(
            """
            UPDATE tasks
            SET title = ?,
                description = ?,
                status = ?,
                deadline = ?,
                importance = ?
            WHERE id = ?
            """,
            (
                new_title.strip(),
                new_description,
                new_status,
                new_deadline,
                new_importance,
                task_id,
            ),
        )

        updated_task = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        return dict(updated_task)


def delete_task(task_id):
    """Menghapus tugas berdasarkan ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )

        return cursor.rowcount > 0
