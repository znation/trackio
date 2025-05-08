import json
import os

import gradio as gr
import pandas as pd
import plotly.express as px

TRACKIO_DIR = "trackio"


def get_projects():
    if not os.path.exists(TRACKIO_DIR):
        return []
    return [
        d
        for d in os.listdir(TRACKIO_DIR)
        if os.path.isdir(os.path.join(TRACKIO_DIR, d))
    ]


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
    run_path = os.path.join(run_dir, "run.parquet")
    config_path = os.path.join(run_dir, "config.json")
    df = None
    config = {}
    if os.path.exists(run_path):
        df = pd.read_parquet(run_path)
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
    return df, config


def plot_metrics(df):
    if df is None or df.empty:
        return None
    plots = []
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        fig = px.line(df, y=col, title=col)
        plots.append(fig)
    return plots


def update_runs(project):
    return gr.Dropdown(choices=get_runs(project), value=None)


def update_dashboard(project, run):
    if not project or not run:
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
        )
    df, config = load_run_data(project, run)
    plots = plot_metrics(df)
    return plots, gr.JSON(value=config), gr.update(visible=True)


def launch_ui():
    with gr.Blocks() as demo:
        gr.Markdown("# Trackio Dashboard")
        with gr.Row():
            project_dd = gr.Dropdown(label="Project", choices=get_projects())
            run_dd = gr.Dropdown(label="Run", choices=[])
        with gr.Row():
            plot_output = gr.LinePlot(
                label="Metrics",
                visible=False,
                show_label=True,
                elem_id="metrics-plot",
                interactive=True,
                scale=2,
            )
            config_output = gr.JSON(label="Config", visible=False)
        # Events
        project_dd.change(
            fn=lambda p: update_runs(p), inputs=project_dd, outputs=run_dd
        )
        run_dd.change(
            fn=lambda p, r: update_dashboard(p, r),
            inputs=[project_dd, run_dd],
            outputs=[plot_output, config_output, plot_output],
        )
    demo.launch()
