import json
import os
import sqlite3

from huggingface_hub import CommitScheduler

try:
    from trackio.dummy_commit_scheduler import DummyCommitScheduler
    from trackio.utils import RESERVED_KEYS, TRACKIO_DIR
except:  # noqa: E722
    from dummy_commit_scheduler import DummyCommitScheduler
    from utils import RESERVED_KEYS, TRACKIO_DIR

HF_TOKEN = os.environ.get("HF_TOKEN")
PERSIST_TO_DATASET = os.environ.get("PERSIST_TO_DATASET")
PERSIST_TO_DATASET_DIR = os.environ.get("PERSIST_TO_DATASET_DIR")
if PERSIST_TO_DATASET is None:
    scheduler = DummyCommitScheduler()
else:
    scheduler = CommitScheduler(
        repo_id=PERSIST_TO_DATASET,
        repo_type="dataset",
        folder_path=TRACKIO_DIR,
        path_in_repo=PERSIST_TO_DATASET_DIR,
        private=True,
        squash_history=True
    )


class SQLiteStorage:
    def __init__(self, project: str, name: str, config: dict):
        self.project = project
        self.name = name
        self.config = config
        self.db_path = os.path.join(TRACKIO_DIR, "trackio.db")

        os.makedirs(TRACKIO_DIR, exist_ok=True)

        self._init_db()
        self._save_config()

    def _init_db(self):
        """Initialize the SQLite database with required tables."""
        with scheduler.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        project_name TEXT NOT NULL,
                        run_name TEXT NOT NULL,
                        metrics TEXT NOT NULL
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS configs (
                        project_name TEXT NOT NULL,
                        run_name TEXT NOT NULL,
                        config TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (project_name, run_name)
                    )
                """)

                conn.commit()

    def _save_config(self):
        """Save the run configuration to the database."""
        with scheduler.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO configs (project_name, run_name, config) VALUES (?, ?, ?)",
                    (self.project, self.name, json.dumps(self.config)),
                )
                conn.commit()

    def log(self, metrics: dict):
        """Log metrics to the database."""
        for k in metrics.keys():
            if k in RESERVED_KEYS or k.startswith("__"):
                raise ValueError(
                    f"Please do not use this reserved key as a metric: {k}"
                )

        with scheduler.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO metrics 
                    (project_name, run_name, metrics)
                    VALUES (?, ?, ?)
                    """,
                    (self.project, self.name, json.dumps(metrics)),
                )
                conn.commit()

    def get_metrics(self, project: str, run: str) -> list[dict]:
        """Retrieve metrics for a specific run."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT timestamp, metrics
                FROM metrics
                WHERE project_name = ? AND run_name = ?
                ORDER BY timestamp
                """,
                (project, run),
            )
            rows = cursor.fetchall()

            results = []
            for row in rows:
                timestamp, metrics_json = row
                metrics = json.loads(metrics_json)
                metrics["timestamp"] = timestamp
                results.append(metrics)

            return results

    def get_projects(self) -> list[str]:
        """Get list of all projects."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT project_name FROM metrics")
            return [row[0] for row in cursor.fetchall()]

    def get_runs(self, project: str) -> list[str]:
        """Get list of all runs for a project."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT run_name FROM metrics WHERE project_name = ?",
                (project,),
            )
            return [row[0] for row in cursor.fetchall()]

    def finish(self):
        """Cleanup when run is finished."""
        pass
