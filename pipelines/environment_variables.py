import os

PRIVATE_TOKEN = os.environ.get("GITLAB_PRIVATE_TOKEN", None)
PROJECT_ID = os.environ.get("GITLAB_PROJECT_ID", None)
REFERENCE = os.environ.get("REFERENCE", None)
URL = os.environ.get("GITLAB_URL", None)
