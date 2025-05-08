import contextvars

from trackio.storage import TrackioStorage
from trackio.utils import generate_readable_name


class Run:
    def __init__(
        self, project: str, name: str | None = None, config: dict | None = None
    ):
        self.project = project
        self.name = name or generate_readable_name()
        self.config = config or {}
        self.storage = TrackioStorage(project, name, config)

    def log(self, metrics: dict):
        self.storage.log(metrics)

    def finish(self):
        self.storage.finish()


current_run: contextvars.ContextVar[Run | None] = contextvars.ContextVar("current_run", default=None)
