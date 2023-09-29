from .. import main
from fastapi.testclient import TestClient

client = TestClient(main.app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_chat_modelate():
    response = client.get(
        "/moderations",
        params={
            "prompt": "これはテストです。",
            "user_id": "test",
            "model": "gpt-3.5-turbo",
            "response_language": "日本語",
        },
    )
    assert response.status_code == 200
    assert "response" in response.json()
