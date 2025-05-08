import json
import os

import pandas as pd
from datasets import Dataset


class TrackioStorage:
    def __init__(self, project: str, name: str, config: dict):
        self.project = project
        self.name = name
        self.config = config
        self.logs: list[dict] = []
        self.dir = os.path.join("trackio", project, self.name)
        os.makedirs(self.dir, exist_ok=True)
        self.run_path = os.path.join(self.dir, "run.parquet")
        self.config_path = os.path.join(self.dir, "config.json")

        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def log(self, metrics: dict):
        self.logs.append(metrics)

    def finish(self):
        if self.logs:
            df = pd.DataFrame(self.logs)
            ds = Dataset.from_pandas(df)
            ds.to_parquet(self.run_path)
