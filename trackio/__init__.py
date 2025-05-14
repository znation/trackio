import contextvars
from pathlib import Path

from gradio_client import Client

from trackio.run import Run
from trackio.ui import demo
from trackio.utils import TRACKIO_DIR

__version__ = Path(__file__).parent.joinpath("version.txt").read_text().strip()


current_run: contextvars.ContextVar[Run | None] = contextvars.ContextVar(
    "current_run", default=None
)
current_project: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_project", default=None
)
current_server: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_server", default=None
)

config = {}


def init(project: str, name: str | None = None, config: dict | None = None) -> Run:
    if not current_server.get():
        url = demo.launch(show_api=False, inline=False, quiet=True, prevent_thread_lock=True)
        current_server.set(url)
    else:
        url = current_server.get()
    if current_project.get() is None or current_project.get() != project:
        print(f"* Trackio project initialized: {project}")
        print(f"* Trackio metrics logged to: {TRACKIO_DIR}")
        print(f"* View dashboard by running: trackio show --project {project}")

    current_project.set(project)
    client = Client(url, verbose=False)
    run = Run(project=project, client=client, name=name, config=config)
    current_run.set(run)
    globals()["config"] = run.config
    return run


def log(metrics):
    if current_run.get() is None:
        raise RuntimeError("Call trackio.init() before log().")
    current_run.get().log(metrics)


def finish():
    if current_run.get() is None:
        raise RuntimeError("Call trackio.init() before finish().")
    current_run.get().finish()
