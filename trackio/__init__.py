import contextvars
from pathlib import Path

from gradio_client import Client

from trackio.run import Run
from trackio.ui import launch_gradio

__version__ = Path(__file__).parent.joinpath("version.txt").read_text().strip()


current_run: contextvars.ContextVar[Run | None] = contextvars.ContextVar(
    "current_run", default=None
)

current_server: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_server", default=None
)

config = {}


def init(project, name=None, config=None):
    if not current_server.get():
        url = launch_gradio(show_api=False, inline=False, quiet=True)
        print(f"* Trackio server launched at: {url}")
        print(f"** View project dashboard at: {url}?project={project}")
        current_server.set(url)
    else:
        url = current_server.get()
    client = Client(url, verbose=False)
    run = Run(project=project, client=client, name=name, config=config)
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
