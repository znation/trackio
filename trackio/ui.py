from typing import Any

import gradio as gr
import pandas as pd

from trackio.sqlite_storage import SQLiteStorage
from trackio.utils import RESERVED_KEYS


def get_projects(request: gr.Request):
    storage = SQLiteStorage("", "", {})
    projects = storage.get_projects()
    if project := request.query_params.get("project"):
        pass
    else:
        project = projects[0] if projects else None
    return gr.Dropdown(
        label="Project",
        choices=projects,
        value=project,
        allow_custom_value=True,
    )


def get_runs(project):
    if not project:
        return []
    storage = SQLiteStorage("", "", {})
    return storage.get_runs(project)


def load_run_data(project, run):
    if not project or not run:
        return None
    storage = SQLiteStorage("", "", {})
    metrics = storage.get_metrics(project, run)
    if not metrics:
        return None
    df = pd.DataFrame(metrics)
    if "step" not in df.columns:
        df["step"] = range(len(df))
    return df


def update_runs(project):
    if project is None:
        runs = []
    else:
        runs = get_runs(project)
    return gr.Dropdown(choices=runs, value=runs)


def toggle_timer(cb_value):
    if cb_value:
        return gr.Timer(active=True)
    else:
        return gr.Timer(active=False)


def log(project: str, run: str, metrics: dict[str, Any]) -> None:
    storage = SQLiteStorage(project, run, {})
    storage.log(metrics)


with gr.Blocks(theme="citrus") as demo:
    with gr.Sidebar():
        gr.Markdown("# 🎯 Trackio Dashboard")
        project_dd = gr.Dropdown(label="Project")
        gr.Markdown("### ⚙️ Settings")
        realtime_cb = gr.Checkbox(label="Refresh realtime", value=True)
    with gr.Row():
        run_dd = gr.Dropdown(label="Run", choices=[], multiselect=True)

    timer = gr.Timer(value=1)

    gr.on(
        [demo.load, timer.tick],
        fn=get_projects,
        outputs=project_dd,
        show_progress="hidden",
    )
    gr.on(
        [demo.load, project_dd.change, timer.tick],
        fn=update_runs,
        inputs=project_dd,
        outputs=run_dd,
        show_progress="hidden",
    )
    realtime_cb.change(
        fn=toggle_timer,
        inputs=realtime_cb,
        outputs=timer,
        api_name="toggle_timer",
    )

    gr.api(
        fn=log,
        api_name="log",
    )

    @gr.render(
        triggers=[run_dd.change, timer.tick],
        inputs=[project_dd, run_dd],
    )
    def update_dashboard(project, runs):
        dfs = []
        for run in runs:
            df = load_run_data(project, run)
            if df is not None:
                df["run"] = run
                dfs.append(df)
        if dfs:
            master_df = pd.concat(dfs, ignore_index=True)
        else:
            master_df = pd.DataFrame()
        numeric_cols = master_df.select_dtypes(include="number").columns
        numeric_cols = [c for c in numeric_cols if c not in RESERVED_KEYS]
        for col in numeric_cols:
            gr.LinePlot(
                master_df,
                x="step",
                y=col,
                color="run" if "run" in master_df.columns else None,
                title=col,
            )


def launch_gradio(**kwargs) -> str:
    _, url, _ = demo.launch(**kwargs)
    return url


if __name__ == "__main__":
    launch_gradio()
