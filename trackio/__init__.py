from pathlib import Path

from .storage import TrackioStorage
from .ui import launch_ui

__version__ = Path(__file__).parent.joinpath("version.txt").read_text().strip()

_current_run = None


class Run:
    def __init__(self, project, name, config):
        self.project = project
        self.name = name
        self.config = config
        self.storage = TrackioStorage(project, name, config)

    def log(self, metrics):
        self.storage.log(metrics)

    def finish(self):
        self.storage.finish()


def init(project, name=None, config=None):
    global _current_run
    _current_run = Run(project, name, config)
    return _current_run


def log(metrics):
    if _current_run is None:
        raise RuntimeError("Call trackio.init() before log().")
    _current_run.log(metrics)


def finish():
    if _current_run is None:
        raise RuntimeError("Call trackio.init() before finish().")
    _current_run.finish()
    global _current_run
    _current_run = None


def ui():
    launch_ui()
