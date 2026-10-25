import time

import pytest
import main


@pytest.fixture(autouse=True)
def reset_pending_deletions(monkeypatch):
    """Isolate confirmation tokens between tests."""
    monkeypatch.setattr(main, "pending_deletions", {})


@pytest.fixture
def sample_task():
    return {
        "id": 501,
        "title": "TEST AI INTEGRATION",
        "description": None,
        "status": "pending",
        "importance": "high",
        "deadline": None,
    }


def test_create_task_parses_title_and_importance(monkeypatch, sample_task):
    created = {}

    def fake_create_task(**kwargs):
        created.update(kwargs)
        return {**sample_task, **kwargs}

    events = []
    monkeypatch.setattr(main.crud, "create_task", fake_create_task)
    monkeypatch.setattr(main, "send_n8n_event", lambda event, task: events.append((event, task)))

    result = main.handle_task_command(
        "Buat tugas TEST AI INTEGRATION dengan importance high"
    )

    assert result["action"] == "create_task"
    assert created["title"] == "TEST AI INTEGRATION"
    assert created["importance"] == "high"
    assert events and events[0][0] == "task.created"


def test_update_status_by_title(monkeypatch, sample_task):
    updated = {**sample_task, "status": "in_progress"}
    monkeypatch.setattr(main.crud, "get_all_tasks", lambda: [sample_task])
    monkeypatch.setattr(main.crud, "update_task", lambda **kwargs: updated)
    events = []
    monkeypatch.setattr(main, "send_n8n_event", lambda event, task: events.append(event))

    result = main.handle_task_command(
        "Ubah status tugas TEST AI INTEGRATION menjadi in_progress"
    )

    assert result["action"] == "update_task"
    assert result["task"]["status"] == "in_progress"
    assert events == ["task.updated"]


def test_delete_by_title_requests_confirmation_without_deleting(
    monkeypatch, sample_task
):
    monkeypatch.setattr(main.crud, "get_all_tasks", lambda: [sample_task])

    def unexpected_delete(*args, **kwargs):
        pytest.fail("Task must not be deleted before confirmation")

    monkeypatch.setattr(main.crud, "delete_task", unexpected_delete)

    result = main.handle_task_command("Hapus tugas TEST AI INTEGRATION")

    assert result["action"] == "confirmation_required"
    assert "konfirmasi hapus " in result["reply"].lower()
    assert len(main.pending_deletions) == 1


def test_valid_delete_confirmation_deletes_and_emits_event(
    monkeypatch, sample_task
):
    token = "valid_test_token"
    main.pending_deletions[token] = {
        "task_id": sample_task["id"],
        "expires_at": time.time() + 300,
    }
    monkeypatch.setattr(main.crud, "get_task_by_id", lambda task_id: sample_task)
    monkeypatch.setattr(main.crud, "delete_task", lambda task_id: True)
    events = []
    monkeypatch.setattr(main, "send_n8n_event", lambda event, task: events.append(event))

    result = main.handle_task_command(f"konfirmasi hapus {token}")

    assert result["action"] == "delete_task"
    assert events == ["task.deleted"]
    assert token not in main.pending_deletions


def test_expired_delete_confirmation_is_rejected(monkeypatch, sample_task):
    token = "expired_test_token"
    main.pending_deletions[token] = {
        "task_id": sample_task["id"],
        "expires_at": time.time() - 1,
    }
    monkeypatch.setattr(main.crud, "delete_task", lambda task_id: pytest.fail("Must not delete"))
    events = []
    monkeypatch.setattr(main, "send_n8n_event", lambda event, task: events.append(event))

    result = main.handle_task_command(f"konfirmasi hapus {token}")

    assert result["action"] == "delete_expired"
    assert token not in main.pending_deletions
    assert events == []


def test_invalid_delete_confirmation_is_rejected(monkeypatch):
    monkeypatch.setattr(main.crud, "delete_task", lambda task_id: pytest.fail("Must not delete"))
    events = []
    monkeypatch.setattr(main, "send_n8n_event", lambda event, task: events.append(event))

    result = main.handle_task_command("konfirmasi hapus not_a_real_token")

    assert result["action"] == "delete_rejected"
    assert events == []


def test_duplicate_titles_are_not_updated(monkeypatch, sample_task):
    duplicate = {**sample_task, "id": 502}
    monkeypatch.setattr(main.crud, "get_all_tasks", lambda: [sample_task, duplicate])
    monkeypatch.setattr(main.crud, "update_task", lambda **kwargs: pytest.fail("Must not update"))
    events = []
    monkeypatch.setattr(main, "send_n8n_event", lambda event, task: events.append(event))

    result = main.handle_task_command(
        "Ubah status tugas TEST AI INTEGRATION menjadi in_progress"
    )

    assert result["action"] == "none"
    assert events == []


def test_unrecognized_message_returns_none():
    result = main.handle_task_command("Jelaskan cara mengatur jadwal kerja")
    assert result is None
