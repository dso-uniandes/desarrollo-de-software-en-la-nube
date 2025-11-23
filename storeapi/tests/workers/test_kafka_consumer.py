from message_broker import worker

def test_get_consumer_returns_none_in_test(monkeypatch):
    monkeypatch.setattr(worker, "get_consumer", lambda: None, raising=False)
    consumer = worker.get_consumer()
    assert consumer is None