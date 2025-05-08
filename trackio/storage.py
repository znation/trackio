import csv
import json
import os

from trackio.utils import RESERVED_KEYS, TRACKIO_DIR


class TrackioStorage:
    def __init__(self, project: str, name: str, config: dict):
        self.project = project
        self.name = name
        self.config = config
        self.dir = os.path.join(TRACKIO_DIR, project, self.name)
        os.makedirs(self.dir, exist_ok=True)
        self.csv_path = os.path.join(self.dir, "run.csv")
        self.parquet_path = os.path.join(self.dir, "run.parquet")
        self.config_path = os.path.join(self.dir, "config.json")
        self.headers = []

        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def log(self, metrics: dict):
        for k in metrics.keys():
            if k in RESERVED_KEYS or k.startswith("__"):
                raise ValueError(
                    f"Please do not use this reserved key as a metric: {k}"
                )

        if not os.path.exists(self.csv_path) or os.path.getsize(self.csv_path) == 0:
            self.headers = list(metrics.keys())
            with open(self.csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()
                writer.writerow(metrics)
            return

        new_keys = [k for k in metrics.keys() if k not in self.headers]
        if new_keys:
            self.headers.extend(new_keys)
            # Read all existing rows, add new keys, and fill with empty strings
            # Write back with new headers. This way, the CSV remains valid.
            with open(self.csv_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            with open(self.csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()
                for row in rows:
                    for k in new_keys:
                        row[k] = ""
                    writer.writerow(row)
                full_row = {h: metrics.get(h, "") for h in self.headers}
                writer.writerow(full_row)
        else:
            with open(self.csv_path, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writerow({h: metrics.get(h, "") for h in self.headers})

    def finish(self):
        pass
        # if self.logs:
        #     df = pd.DataFrame(self.logs)
        #     ds = Dataset.from_pandas(df)
        #     ds.to_parquet(self.run_path)
