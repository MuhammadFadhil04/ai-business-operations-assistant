"""Backend tests. Run: python -m pip install pytest httpx && python -m pytest -v"""
from datetime import datetime, timedelta
from types import SimpleNamespace
from urllib.error import URLError
import pytest
from fastapi.testclient import TestClient
import main
import crud
import database


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("N8N_WEBHOOK_URL", raising=False)
    monkeypatch.delenv("N8N_WEBHOOK_SECRET", raising=False)
    return TestClient(main.app)


def test_home(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "success"


def test_health(client):
    assert client.get("/health").json()["status"] == "healthy"


def test_create_task(client, monkeypatch):
    monkeypatch.setattr(crud, "create_task", lambda **kw: {
        "id": 9001, "title": kw["title"], "description": kw.get("description"),
        "status": "pending", "deadline": kw.get("deadline"),
        "importance": kw.get("importance", "normal")
    })
    r = client.post("/tasks", json={"title": "Tes otomatis", "importance": "high"})
    assert r.status_code == 201
    assert r.json()["importance"] == "high"


def test_create_rejects_blank_title(client):
    assert client.post("/tasks", json={"title": "   "}).status_code == 422


def test_create_rejects_invalid_importance(client):
    assert client.post("/tasks", json={"title": "Tes", "importance": "urgent"}).status_code == 422


def test_create_rejects_invalid_deadline(client):
    assert client.post("/tasks", json={"title": "Tes", "deadline": "bukan-tanggal"}).status_code == 422


def test_list_tasks(client, monkeypatch):
    sample = [{"id": 1, "title": "Tes", "status": "pending"}]
    monkeypatch.setattr(crud, "get_all_tasks", lambda: sample)
    assert client.get("/tasks").json() == sample


def test_missing_task_returns_404(client, monkeypatch):
    monkeypatch.setattr(crud, "get_task_by_id", lambda task_id: None)
    assert client.get("/tasks/999999").status_code == 404


def test_patch_task(client, monkeypatch):
    updated = {"id": 5, "title": "Tes", "description": None,
               "status": "completed", "deadline": None, "importance": "normal"}
    monkeypatch.setattr(crud, "update_task", lambda task_id, **kw: updated)
    events = []
    monkeypatch.setattr(main, "send_n8n_event", lambda event, task: events.append((event, task["id"])))
    r = client.patch("/tasks/5", json={"status": "completed"})
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
    assert events == [("task.updated", 5)]


def test_patch_rejects_empty_update(client):
    assert client.patch("/tasks/5", json={}).status_code == 400


def test_patch_rejects_invalid_status(client):
    assert client.patch("/tasks/5", json={"status": "finished"}).status_code == 422


def test_delete_task(client, monkeypatch):
    task = {"id": 6, "title": "Tes hapus", "description": None,
            "status": "pending", "deadline": None, "importance": "normal"}
    monkeypatch.setattr(crud, "get_task_by_id", lambda task_id: task)
    monkeypatch.setattr(crud, "delete_task", lambda task_id: True)
    events = []
    monkeypatch.setattr(main, "send_n8n_event", lambda event, item: events.append((event, item["id"])))
    r = client.delete("/tasks/6")
    assert r.status_code == 200
    assert r.json()["task_id"] == 6
    assert events == [("task.deleted", 6)]


def test_priority_uses_60_40_weights():
    deadline = (datetime.now() + timedelta(days=10)).isoformat(timespec="seconds")
    result = main.calculate_task_priority({
        "status": "pending", "deadline": deadline, "importance": "normal"
    })
    assert result["deadline_score"] == 25
    assert result["importance_score"] == 60
    assert result["score"] == 39


def test_completed_task_has_zero_priority():
    result = main.calculate_task_priority({
        "status": "completed", "deadline": None, "importance": "high"
    })
    assert result["score"] == 0
    assert result["level"] == "completed"


def test_in_progress_bonus():
    deadline = (datetime.now() + timedelta(days=10)).isoformat(timespec="seconds")
    result = main.calculate_task_priority({
        "status": "in_progress", "deadline": deadline, "importance": "normal"
    })
    assert result["score"] == 44
    assert "Tambahan 5 poin" in result["reason"]


def test_overdue_task_is_critical():
    deadline = (datetime.now() - timedelta(days=1)).isoformat(timespec="seconds")
    result = main.calculate_task_priority({
        "status": "pending", "deadline": deadline, "importance": "low"
    })
    assert result["score"] == 100
    assert result["level"] == "critical"


def test_prioritized_endpoint(client, monkeypatch):
    tasks = [
        {"id": 1, "title": "Tanpa deadline", "status": "pending", "deadline": None, "importance": "low"},
        {"id": 2, "title": "Terlambat", "status": "pending",
         "deadline": (datetime.now() - timedelta(days=1)).isoformat(timespec="seconds"), "importance": "high"},
        {"id": 3, "title": "Selesai", "status": "completed", "deadline": None, "importance": "high"},
    ]
    monkeypatch.setattr(crud, "get_all_tasks", lambda: tasks)
    r = client.get("/tasks/prioritized")
    assert r.status_code == 200
    data = r.json()
    assert data["total_tasks"] == 3
    assert data["active_tasks"] == 2
    assert data["tasks"][0]["id"] == 2
    assert data["tasks"][-1]["id"] == 3


def test_duplicate_detection_endpoint(client, monkeypatch):
    tasks = [
        {"id": 1, "title": "Laporan", "description": "Bulanan"},
        {"id": 2, "title": " laporan ", "description": "bulanan"},
        {"id": 3, "title": "Presentasi", "description": ""},
    ]
    monkeypatch.setattr(crud, "get_all_tasks", lambda: tasks)
    data = client.get("/tasks/duplicates").json()
    assert data["total_groups"] == 1
    assert data["duplicates"][0]["task_ids"] == [1, 2]


def test_create_rejects_description_over_2000_characters(client):
    response = client.post(
        "/tasks",
        json={"title": "Tes", "description": "x" * 2001},
    )
    assert response.status_code == 422


def test_patch_rejects_description_over_2000_characters(client):
    response = client.patch(
        "/tasks/5",
        json={"description": "x" * 2001},
    )
    assert response.status_code == 422


def test_chat_rejects_whitespace_only_message(client, monkeypatch):
    monkeypatch.setattr(main, "gemini_client", object())
    response = client.post("/ai/chat", json={"message": "   "})
    assert response.status_code == 400


def test_chat_rejects_message_over_4000_characters(client):
    response = client.post("/ai/chat", json={"message": "x" * 4001})
    assert response.status_code == 422


@pytest.mark.parametrize(
    ("error_code", "expected_status"),
    [(429, 429), (503, 503), (500, 502)],
)
def test_chat_maps_gemini_errors_without_returning_provider_details(
    client, monkeypatch, error_code, expected_status
):
    diagnostic = "private-provider-diagnostic"

    class FakeGeminiError(Exception):
        code = error_code

    def fail_generate_content(**kwargs):
        raise FakeGeminiError(diagnostic)

    monkeypatch.setattr(crud, "get_all_tasks", lambda: [])
    monkeypatch.setattr(
        main,
        "gemini_client",
        SimpleNamespace(
            models=SimpleNamespace(generate_content=fail_generate_content)
        ),
    )

    response = client.post("/ai/chat", json={"message": "Bantu susun prioritas"})

    assert response.status_code == expected_status
    assert diagnostic not in response.text


def test_create_task_succeeds_when_n8n_is_unavailable(
    client, monkeypatch
):
    task = {
        "id": 77,
        "title": "Tes webhook terputus",
        "description": None,
        "status": "pending",
        "deadline": None,
        "importance": "normal",
    }
    monkeypatch.setattr(crud, "create_task", lambda **kwargs: task)
    monkeypatch.setenv("N8N_WEBHOOK_URL", "https://n8n.invalid/webhook")
    monkeypatch.setenv("N8N_WEBHOOK_SECRET", "test-only-secret")

    def fail_urlopen(*args, **kwargs):
        raise URLError("simulated n8n connection failure")

    monkeypatch.setattr(main.urllib.request, "urlopen", fail_urlopen)

    response = client.post("/tasks", json={"title": task["title"]})

    assert response.status_code == 201
    assert response.json()["id"] == task["id"]


def test_sqlite_task_persists_after_database_reinitialization(
    tmp_path, monkeypatch
):
    database_path = tmp_path / "persistent-test.db"
    monkeypatch.setattr(database, "DATABASE_PATH", database_path)

    database.init_db()
    task = crud.create_task(
        title="Tes persistensi",
        description="Tugas tetap tersedia setelah init ulang.",
        importance="high",
    )

    database.init_db()

    assert crud.get_task_by_id(task["id"]) == task
