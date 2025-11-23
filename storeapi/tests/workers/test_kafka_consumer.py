from message_broker import worker

def test_get_consumer_returns_none_in_test(monkeypatch):
    monkeypatch.setattr(worker.config, "ENV_STATE", "test")
    consumer = worker.get_consumer()
    assert consumer is None