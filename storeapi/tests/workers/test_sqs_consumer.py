from message_broker import client

def test_get_sqs_client_returns_none_in_test(monkeypatch):
    monkeypatch.setattr(client.config, "ENV_STATE", "test")
    sqs_client = client.get_sqs_client()
    assert sqs_client is None