from message_broker import worker

def test_get_consumer_returns_none_in_test(monkeypatch):
    monkeypatch.setattr(worker.config, "ENV_STATE", "test")
    consumer = worker.getConsumer()
    assert consumer is None