import contextvars
import webbrowser
from pathlib import Path
import time

from gradio_client import Client
from huggingface_hub.errors import RepositoryNotFoundError
from httpx import ReadTimeout

from trackio.deploy import deploy_as_space
from trackio.run import Run
from trackio.ui import demo
from trackio.utils import TRACKIO_DIR, TRACKIO_LOGO_PATH, block_except_in_notebook

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


def init(
    project: str, name: str | None = None, space_id=None, config: dict | None = None
) -> Run:
    if not current_server.get():
        if space_id is None:
            _, url, _ = demo.launch(
                show_api=False, inline=False, quiet=True, prevent_thread_lock=True
            )
        else:
            url = space_id
        current_server.set(url)
    else:
        url = current_server.get()

    client = None
    try:
        client = Client(url, verbose=False)
    except RepositoryNotFoundError as e:
        # if we're passed a space_id, ignore the error here, otherwise re-raise it
        if space_id is None:
            raise e
    if client is None and space_id is not None:
        # try to create the space on demand
        deploy_as_space(space_id)
        # try to wait until the Client can initialize
        max_attempts = 30
        attempts = 0
        while client is None:
            try:
                client = Client(space_id, verbose=False)
            except ReadTimeout:
                print("Space is not yet ready. Waiting 5 seconds...")
                time.sleep(5)
            except ValueError as e:
                print(f"Space gave error {e}. Trying again in 5 seconds...")
                time.sleep(5)
            attempts += 1
            if attempts >= max_attempts:
                break

    if current_project.get() is None or current_project.get() != project:
        print(f"* Trackio project initialized: {project}")
        if space_id is None:
            print(f"* Trackio metrics logged to: {TRACKIO_DIR}")
            print(
                f'\n* View dashboard by running in your terminal: trackio show --project "{project}"'
            )
            print(f'* or by running in Python: trackio.show(project="{project}")')
        else:
            print(
                f"* Trackio metrics logged to: https://huggingface.co/spaces/{space_id}"
            )
    current_project.set(project)

    run = Run(project=project, client=client, name=name, config=config)
    current_run.set(run)
    globals()["config"] = run.config
    return run


def log(metrics: dict) -> None:
    if current_run.get() is None:
        raise RuntimeError("Call trackio.init() before log().")
    current_run.get().log(metrics)


def finish():
    if current_run.get() is None:
        raise RuntimeError("Call trackio.init() before finish().")
    current_run.get().finish()


def show(project: str | None = None):
    _, url, share_url = demo.launch(
        show_api=False,
        quiet=True,
        inline=False,
        prevent_thread_lock=True,
        favicon_path=TRACKIO_LOGO_PATH,
        allowed_paths=[TRACKIO_LOGO_PATH],
    )
    base_url = share_url + "/" if share_url else url
    dashboard_url = base_url + f"?project={project}" if project else base_url
    print(f"* Trackio UI launched at: {dashboard_url}")
    webbrowser.open(dashboard_url)
    block_except_in_notebook()
