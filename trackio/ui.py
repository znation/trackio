from typing import Any

import gradio as gr
import pandas as pd

from trackio.sqlite_storage import SQLiteStorage
from trackio.utils import RESERVED_KEYS, TRACKIO_LOGO_PATH


def get_projects(request: gr.Request):
    storage = SQLiteStorage("", "", {})
    projects = storage.get_projects()
    if project := request.query_params.get("project"):
        interactive = False
    else:
        interactive = True
        project = projects[0] if projects else None
    return gr.Dropdown(
        label="Project",
        choices=projects,
        value=project,
        allow_custom_value=True,
        interactive=interactive,
    )


def get_runs(project):
    if not project:
        return []
    storage = SQLiteStorage("", "", {})
    return storage.get_runs(project)


def load_run_data(project: str | None, run: str | None, smoothing: bool):
    if not project or not run:
        return None
    storage = SQLiteStorage("", "", {})
    metrics = storage.get_metrics(project, run)
    if not metrics:
        return None
    df = pd.DataFrame(metrics)
    if smoothing:
        numeric_cols = df.select_dtypes(include="number").columns
        numeric_cols = [c for c in numeric_cols if c not in RESERVED_KEYS]
        df[numeric_cols] = df[numeric_cols].ewm(alpha=0.1).mean()
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


def configure(request: gr.Request):
    if metrics := request.query_params.get("metrics"):
        return metrics.split(",")
    else:
        return []


with gr.Blocks(theme="citrus", title="Trackio Dashboard") as demo:
    with gr.Sidebar() as sidebar:
        gr.Markdown(
            f"<div style='display: flex; align-items: center; gap: 8px;'><img src='/gradio_api/file={TRACKIO_LOGO_PATH}' width='32' height='32'><span style='font-size: 2em; font-weight: bold;'>Trackio</span></div>"
        )
        project_dd = gr.Dropdown(label="Project", allow_custom_value=True)
        gr.Markdown("### ⚙️ Settings")
        realtime_cb = gr.Checkbox(label="Refresh realtime", value=True)
        smoothing_cb = gr.Checkbox(label="Smoothing", value=True)
    with gr.Row():
        run_dd = gr.Dropdown(label="Run", choices=[], multiselect=True)

    timer = gr.Timer(value=1)
    metrics_subset = gr.State([])

    gr.on(
        [demo.load],
        fn=configure,
        outputs=metrics_subset,
    )
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

    x_lim = gr.State(None)

    def update_x_lim(select_data: gr.SelectData):
        return select_data.index

    @gr.render(
        triggers=[demo.load, run_dd.change, timer.tick, smoothing_cb.change, x_lim.change],
        inputs=[project_dd, run_dd, smoothing_cb, metrics_subset, x_lim],
    )
    def update_dashboard(project, runs, smoothing, metrics_subset, x_lim_value):
        dfs = []
        for run in runs:
            df = load_run_data(project, run, smoothing)
            if df is not None:
                df["run"] = run
                dfs.append(df)
        if dfs:
            master_df = pd.concat(dfs, ignore_index=True)
        else:
            master_df = pd.DataFrame()
        numeric_cols = master_df.select_dtypes(include="number").columns
        numeric_cols = [c for c in numeric_cols if c not in RESERVED_KEYS]
        if metrics_subset:
            numeric_cols = [c for c in numeric_cols if c in metrics_subset]
        with gr.Row(key="row"):
            for col_idx, col in enumerate(numeric_cols):
                plot = gr.LinePlot(
                    master_df,
                    x="step",
                    y=col,
                    color="run" if "run" in master_df.columns else None,
                    title=col,
                    key=f"plot-{col_idx}",
                    preserved_by_key=None,
                    x_lim=x_lim_value,
                    min_width=400,
                )
                plot.select(update_x_lim, outputs=x_lim, key=f"select-{col_idx}")
                plot.double_click(lambda: None, outputs=x_lim, key=f"double-{col_idx}")

if __name__ == "__main__":
    demo.launch(allowed_paths=[TRACKIO_LOGO_PATH])
