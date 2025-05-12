import contextvars
import logging
from pathlib import Path

from trackio.run import Run
from trackio.ui import launch_ui

__version__ = Path(__file__).parent.joinpath("version.txt").read_text().strip()


current_run: contextvars.ContextVar[Run | None] = contextvars.ContextVar(
    "current_run", default=None
)

current_ui: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "ui_running", default=False
)

config = {}

def init(project, name=None, config=None, ui=True):
    logging.info(f"Initializing run | Project: {project} | Name: {name}")
    if ui and not current_ui.get():
        launch_ui()
        current_ui.set(True)
    run = Run(project, name, config)
    current_run.set(run)
    globals()["config"] = run.config


def log(metrics):
    if current_run.get() is None:
        raise RuntimeError("Call trackio.init() before log().")
    current_run.get().log(metrics)


def finish():
    if current_run.get() is None:
        raise RuntimeError("Call trackio.init() before finish().")
    current_run.get().finish()
    current_run.set(None)


def ui():
    launch_ui()
