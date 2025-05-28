# A dummy object to fit the interface of huggingface_hub's CommitScheduler
class DummyCommitScheduler:
    def __init__(self):
        self.lock = None
