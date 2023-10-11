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


# 隠された文字列の統計情報の正常系テスト
def test_data_collection():
    response = client.post(
        "/hidden-text-collection",
        json={
            "user_id": "test",
            "original_text": "これはテストです。",
            "hidden_texts": ["これは", "です。"],
        },
    )
    assert response.status_code == 200

    response = client.post(
        "/hidden-text-collection",
        json={
            "user_id": "test",
            "original_text": "これはテストです。",
            "hidden_texts": ["これは", "です。"],
            "original_text_num": 7,
            "hidden_texts_num": 5,
        },
    )
    assert response.status_code == 200

    response = client.post(
        "/hidden-text-collection",
        json={
            "user_id": "test",
            "original_text": "これはテストです。",
            "hidden_texts": ["これは", "です。"],
            "original_text_num": "7",
            "hidden_texts_num": "5",
        },
    )
    assert response.status_code == 200


# 隠された文字列の統計情報の異常系テスト
def test_error_data_collection():
    response = client.post(
        "/hidden-text-collection",
        json={
            "user_id": "test",
            "original_text": "これはテストです。",
            "hidden_texts": [123, "です。"],
        },
    )
    assert response.status_code == 422

    response = client.post(
        "/hidden-text-collection",
        json={
            "user_id": "test",
            "original_text": "これはテストです。",
            "hidden_texts": "これは",
        },
    )
    assert response.status_code == 422


def test_moderation_suggest():
    response = client.post(
        "/moderations/suggestions",
        json={
            "prompt": "これはテストです。",
            "user_id": "test",
            "model": "gpt-3.5-turbo",
            "response_language": "日本語",
        },
    )
    assert response.status_code == 200
    assert (
        "suggestions" in response.json()
        and type(response.json()["suggestions"]) == list
    )


def test_error_moderation_suggest():
    response = client.post(
        "/moderations/suggestions",
        json={
            "prompt": 123,
            "user_id": "test",
            "model": "gpt-3.5-turbo",
            "response_language": "日本語",
        },
    )
    assert response.status_code == 422
