import os
from typing import Any

import gradio as gr
import huggingface_hub as hf
import pandas as pd

HfApi = hf.HfApi()

try:
    from trackio.sqlite_storage import SQLiteStorage
    from trackio.utils import RESERVED_KEYS, TRACKIO_LOGO_PATH
except:  # noqa: E722
    from sqlite_storage import SQLiteStorage
    from utils import RESERVED_KEYS, TRACKIO_LOGO_PATH


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


def log(project: str, run: str, metrics: dict[str, Any], hf_token: str) -> None:
    if os.getenv("SYSTEM") == "spaces":  # if we are running in Spaces
        # check auth token passed in
        if hf_token is None:
            raise "Expected an hf_token to be provided when logging to a Space"
        who = HfApi.whoami(hf_token)
        owner_name = os.getenv("SPACE_AUTHOR_NAME")
        # make sure the token user is either the author of the space,
        # or is a member of an org that is the author.
        # TODO: we should probably reject read-only or too-fine-grained tokens too...?
        # but the logic to do that would be much more complex b/c of fine-grained tokens.
        orgs = [o["name"] for o in who["orgs"]]
        if owner_name != who["name"] and owner_name not in orgs:
            raise "Expected the provided hf_token to be the user owner of the space, or be a member of the org owner of the space"
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
        triggers=[
            demo.load,
            run_dd.change,
            timer.tick,
            smoothing_cb.change,
            x_lim.change,
        ],
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
        plots: list[gr.LinePlot] = []
        for col in range(len(numeric_cols) // 2):
            with gr.Row(key=f"row-{col}"):
                for i in range(2):
                    plot = gr.LinePlot(
                        master_df,
                        x="step",
                        y=numeric_cols[2 * col + i],
                        color="run" if "run" in master_df.columns else None,
                        title=numeric_cols[2 * col + i],
                        key=f"plot-{col}-{i}",
                        preserved_by_key=None,
                        x_lim=x_lim_value,
                        y_lim=[
                            min(master_df[numeric_cols[2 * col + i]]),
                            max(master_df[numeric_cols[2 * col + i]]),
                        ],
                        show_fullscreen_button=True,
                    )
                    plots.append(plot)

        for plot in plots:
            plot.select(update_x_lim, outputs=x_lim)
            plot.double_click(lambda: None, outputs=x_lim)


if __name__ == "__main__":
    demo.launch(allowed_paths=[TRACKIO_LOGO_PATH])
