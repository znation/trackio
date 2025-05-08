import os

import gradio as gr
import pandas as pd

from trackio.utils import RESERVED_KEYS, TRACKIO_DIR


def get_projects():
    if not os.path.exists(TRACKIO_DIR):
        return []
    projects = sorted(
        [
            d
            for d in os.listdir(TRACKIO_DIR)
            if os.path.isdir(os.path.join(TRACKIO_DIR, d))
        ]
    )
    return gr.Dropdown(
        label="Project", choices=projects, value=projects[0] if projects else None
    )


def get_runs(project):
    project_dir = os.path.join(TRACKIO_DIR, project)
    if not os.path.exists(project_dir):
        return []
    return [
        d
        for d in os.listdir(project_dir)
        if os.path.isdir(os.path.join(project_dir, d))
    ]


def load_run_data(project, run):
    run_dir = os.path.join(TRACKIO_DIR, project, run)
    csv_path = os.path.join(run_dir, "run.csv")
    df = None
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
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


def launch_ui():
    with gr.Blocks(theme="citrus") as demo:
        with gr.Sidebar():
            gr.Markdown("# 🎯 Trackio Dashboard")
            project_dd = gr.Dropdown(label="Project")
            realtime_cb = gr.Checkbox(label="Realtime", value=True)
        with gr.Row():
            run_dd = gr.Dropdown(label="Run", choices=[], multiselect=True)

        timer = gr.Timer(value=1)

        gr.on(
            [demo.load, timer.tick],
            fn=get_projects,
            outputs=project_dd,
            show_progress=False,
        )
        gr.on(
            [demo.load, project_dd.change, timer.tick],
            fn=update_runs,
            inputs=project_dd,
            outputs=run_dd,
            show_progress=False,
        )
        realtime_cb.change(
            fn=toggle_timer,
            inputs=realtime_cb,
            outputs=timer,
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

    demo.launch(show_api=False)


if __name__ == "__main__":
    launch_ui()
