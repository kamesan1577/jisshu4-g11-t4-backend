from .. import main
from fastapi.testclient import TestClient

client = TestClient(main.app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


# ツイートの修正機能の正常系テスト
def test_chat_modelate():
    response = client.post(
        "/moderations",
        json={
            "prompt": "これはテストです。",
            "user_id": "test",
            "model": "gpt-3.5-turbo",
            "response_language": "日本語",
        },
    )
    assert response.status_code == 200
    assert "response" in response.json()

    response = client.post(
        "/moderations",
        json={
            "prompt": ["これはテストです。", "これはテストです。"],
            "user_id": "test",
            "model": "gpt-3.5-turbo",
            "response_language": "日本語",
        },
    )
    assert response.status_code == 200
    assert "response" in response.json()


# ツイートの修正機能の異常系テスト
def test_error_chat_modelate():
    response = client.post(
        "/moderations",
        json={
            "prompt": 123,
            "user_id": "test",
            "model": "gpt-3.5-turbo",
            "response_language": "日本語",
        },
    )
    assert response.status_code == 422
    assert "response" not in response.json()

    response = client.post(
        "/moderations",
        json={
            "prompt": True,
            "user_id": "test",
            "model": "gpt-3.5-turbo",
            "response_language": "日本語",
        },
    )
    assert response.status_code == 422
    assert "response" not in response.json()

    response = client.post(
        "/moderations",
        json={
            "prompt": [True, False],
            "user_id": "test",
            "model": "gpt-3.5-turbo",
            "response_language": "日本語",
        },
    )
    assert response.status_code == 422
    assert "response" not in response.json()

    response = client.post(
        "/moderations",
        json={
            "prompt": ["これはテストです。", 123],
            "user_id": "test",
            "model": "gpt-3.5-turbo",
            "response_language": "日本語",
        },
    )
    assert response.status_code == 422
    assert "response" not in response.json()
