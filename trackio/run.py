import os

from gradio_client import Client

from trackio.utils import generate_readable_name


class Run:
    def __init__(
        self,
        project: str,
        client: Client,
        name: str | None = None,
        config: dict | None = None,
        dataset_id: str | None = None,
    ):
        self.project = project
        self.client = client
        self.name = name or generate_readable_name()
        self.config = config or {}
        self.dataset_id = dataset_id

    def log(self, metrics: dict):
        self.client.predict(
            api_name="/log",
            project=self.project,
            run=self.name,
            metrics=metrics,
            dataset_id=self.dataset_id,
            hf_token=os.getenv("HF_TOKEN", ""),
        )

    def finish(self):
        pass
