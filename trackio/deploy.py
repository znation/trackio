from importlib.resources import files
import os

import huggingface_hub


def deploy_as_space(title: str):
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
    assert(space_id == title) # not sure why these would differ

    hf_api.upload_folder(
        repo_id=space_id,
        repo_type="space",
        folder_path=trackio_path,
    )
