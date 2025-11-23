import sqlite3
from huggingface_hub import HfApi
import wandb
import logging
import os
import datetime
import json


class HuggingFaceLogger:
    def __init__(self, project_name, repository_id=None):
        self.project_name = project_name

        # Set up Hugging Face API
        self.hf_token = os.environ.get("HUGGING_FACE_TOKEN")
        if not self.hf_token:
            raise ValueError("HUGGING_FACE_TOKEN environment variable not set")

        # === DB Setup ===
        self.db_path = os.environ.get("WEATHER_DB_PATH", "weather.db")
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        print(f"[HFLogger] Using DB: {self.db_path} | Exists: {os.path.exists(self.db_path)}")

        # Hugging Face API setup
        self.api = HfApi(token=self.hf_token)

        if repository_id is None:
            self.user_info = self.api.whoami()
            self.username = self.user_info["name"]
            self.repository_id = f"{self.username}/{project_name}"
        else:
            self.repository_id = repository_id

        # Create repo if not exists
        try:
            self.api.repo_info(repo_id=self.repository_id)
        except Exception:
            self.api.create_repo(repo_id=self.repository_id, private=True)

        # Logging setup
        self.logger = logging.getLogger(project_name)
        self.logger.setLevel(logging.INFO)

        # Optional W&B setup
        self.use_wandb = False

    def setup_wandb(self, wandb_api_key, wandb_project=None):
        os.environ["WANDB_API_KEY"] = wandb_api_key
        wandb.init(project=wandb_project or self.project_name)
        self.use_wandb = True

    def log_metrics(self, metrics, step=None):
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "step": step,
            "metrics": metrics
        }

        os.makedirs("logs", exist_ok=True)
        log_filename = f"logs/{timestamp.replace(':', '-')}.json"
        with open(log_filename, "w") as f:
            json.dump(log_entry, f, indent=2)

        self.api.upload_file(
            path_or_fileobj=log_filename,
            path_in_repo=f"logs/{os.path.basename(log_filename)}",
            repo_id=self.repository_id,
            commit_message=f"Log metrics at step {step}"
        )

        if self.use_wandb:
            wandb.log(metrics, step=step)

        self.logger.info(f"Metrics at step {step}: {metrics}")

    def log_model(self, model_path, commit_message=None):
        self.api.upload_folder(
            folder_path=model_path,
            path_in_repo=f"models/{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}",
            repo_id=self.repository_id,
            commit_message=commit_message or f"Upload model at {datetime.datetime.now().isoformat()}"
        )
