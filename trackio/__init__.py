import logging
from pathlib import Path

from trackio.run import Run, current_run
from trackio.ui import launch_ui

__version__ = Path(__file__).parent.joinpath("version.txt").read_text().strip()


def init(project, name=None, config=None):
    logging.info(f"Initializing run | Project: {project} | Name: {name}")
    current_run.set(Run(project, name, config))


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
