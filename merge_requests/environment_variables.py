import os

PRIVATE_TOKEN = os.environ.get("GITLAB_PRIVATE_TOKEN", None)
PROJECT_ID = os.environ.get("GITLAB_PROJECT_ID", None)
SOURCE_BRANCH = os.environ.get("GITLAB_SOURCE_BRANCH", None)
TARGET_BRANCH = os.environ.get("GITLAB_TARGET_BRANCH", None)
MR_TITLE = os.environ.get("GITLAB_MR_TITLE", None)
MR_DESCRIPTION = os.environ.get("GITLAB_MR_DESCRIPTION", None)
ASSIGNEE_ID = os.environ.get("GITLAB_ASSIGNEE_ID", None)
MILESTONE_ID = os.environ.get("GITLAB_MILESTONE_ID", None)
URL = os.environ.get("GITLAB_URL", None)
