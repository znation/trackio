import io
import os
from importlib.resources import files
from pathlib import Path

import gradio
import huggingface_hub


def deploy_as_space(
    title: str,
    persistent_dataset: str | None = None,
    persistent_dataset_dir: str | None = None,
):
    if (
        os.getenv("SYSTEM") == "spaces"
    ):  # in case a repo with this function is uploaded to spaces
        return

    trackio_path = files("trackio")

    hf_api = huggingface_hub.HfApi()
    whoami = None
    login = False
    try:
        whoami = hf_api.whoami()
        if whoami["auth"]["accessToken"]["role"] != "write":
            login = True
    except OSError:
        login = True
    if login:
        print("Need 'write' access token to create a Spaces repo.")
        huggingface_hub.login(add_to_git_credential=False)
        whoami = hf_api.whoami()

    space_id = huggingface_hub.create_repo(
        title,
        space_sdk="gradio",
        repo_type="space",
        exist_ok=True,
    ).repo_id
    assert space_id == title  # not sure why these would differ

    with open(Path(trackio_path, "README.md"), "r") as f:
        readme_content = f.read()
        readme_content = readme_content.replace("{GRADIO_VERSION}", gradio.__version__)
        readme_buffer = io.BytesIO(readme_content.encode("utf-8"))
        hf_api.upload_file(
            path_or_fileobj=readme_buffer,
            path_in_repo="README.md",
            repo_id=space_id,
            repo_type="space",
        )

    huggingface_hub.utils.disable_progress_bars()
    hf_api.upload_folder(
        repo_id=space_id,
        repo_type="space",
        folder_path=trackio_path,
        ignore_patterns=["README.md"],
    )

    # add HF_TOKEN so we have access to dataset to persist data
    HF_TOKEN = os.environ.get("HF_TOKEN")
    if HF_TOKEN is not None:
        huggingface_hub.add_space_secret(space_id, "HF_TOKEN", HF_TOKEN)
    if persistent_dataset is not None:
        huggingface_hub.add_space_variable(
            space_id, "PERSIST_TO_DATASET", persistent_dataset
        )
    if persistent_dataset_dir is not None:
        huggingface_hub.add_space_variable(
            space_id, "PERSIST_TO_DATASET_DIR", persistent_dataset_dir
        )
