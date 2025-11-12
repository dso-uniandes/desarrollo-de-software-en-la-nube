from message_broker import tasks_dispatcher

def test_task_dispatcher_skips_in_test_env(monkeypatch, mocker):
    monkeypatch.setattr(tasks_dispatcher.config, "ENV_STATE", "test")
    # Mock SQS client to ensure it is not called
    monkeypatch.setattr(tasks_dispatcher, "sqs", None)
    spy = mocker.spy(tasks_dispatcher.logger, "info")
    # This should not raise an exception
    tasks_dispatcher.dispatch_task([{"video_id": 1, "task": "process"}], topic="video_tasks")
    
    assert spy.call_count == 1