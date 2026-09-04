from types import SimpleNamespace

from fastapi.testclient import TestClient

import api.main as api


class FakeChat:
    def __init__(self):
        self.messages = []

    def send_message(self, prompt):
        self.messages.append(prompt)
        return SimpleNamespace(text=f"reply {len(self.messages)}")


class FakeClient:
    def __init__(self):
        self.chats_created = []

    def create(self, **kwargs):
        chat = FakeChat()
        self.chats_created.append((kwargs, chat))
        return chat


def test_chat_context_and_session_isolation(monkeypatch):
    fake_client = FakeClient()

    class FakeSessions:
        def __init__(self):
            self.chats = {}

        def get_or_create(self, session_id):
            if session_id not in self.chats:
                self.chats[session_id] = fake_client.create(model=api.MODEL_NAME)
            return self.chats[session_id]

    monkeypatch.setattr(api, "sessions", FakeSessions())
    client = TestClient(api.app)

    first = client.post(
        "/chat",
        json={
            "session_id": "user-a",
            "message": "How should I start?",
            "context": {
                "fitness_goal": {"goal": "strength"},
                "calorie_prediction": {"predicted_calories": 300},
                "secret": "must not reach Gemini",
            },
        },
    )
    second = client.post(
        "/chat",
        json={"session_id": "user-a", "message": "What next?"},
    )
    other_user = client.post(
        "/chat",
        json={"session_id": "user-b", "message": "Hello"},
    )

    assert first.status_code == 200
    assert second.json()["response"] == "reply 2"
    assert other_user.json()["response"] == "reply 1"
    first_prompt = fake_client.chats_created[0][1].messages[0]
    assert "predicted_calories" in first_prompt
    assert "must not reach Gemini" not in first_prompt


def test_gemini_failure_is_sanitized(monkeypatch):
    class FailingChat:
        def send_message(self, prompt):
            raise RuntimeError("GEMINI_API_KEY=secret internal failure")

    class FailingSessions:
        def get_or_create(self, session_id):
            return FailingChat()

    monkeypatch.setattr(api, "sessions", FailingSessions())
    response = TestClient(api.app).post(
        "/chat", json={"session_id": "failure", "message": "test"}
    )

    assert response.status_code == 502
    assert "GEMINI_API_KEY" not in response.text
    assert "secret" not in response.text


def test_chat_validates_empty_and_oversized_messages():
    client = TestClient(api.app)

    empty = client.post("/chat", json={"message": "   "})
    oversized = client.post("/chat", json={"message": "x" * 4001})

    assert empty.status_code == 422
    assert oversized.status_code == 422
