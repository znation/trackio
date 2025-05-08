import os
from datasets import Dataset
import pandas as pd


class TrackioStorage:
    def __init__(self, project, name, config):
        self.project = project
        self.name = name or "unnamed_run"
        self.config = config or {}
        self.logs = []
        self.dir = os.path.join("trackio", project, self.name)
        os.makedirs(self.dir, exist_ok=True)
        self.run_path = os.path.join(self.dir, "run.parquet")
        self.config_path = os.path.join(self.dir, "config.json")
        # Save config immediately
        import json

        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def log(self, metrics):
        self.logs.append(metrics)

    def finish(self):
        if self.logs:
            df = pd.DataFrame(self.logs)
            ds = Dataset.from_pandas(df)
            ds.to_parquet(self.run_path)
