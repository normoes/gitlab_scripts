"""
Goal:
  * Get empty MRs.
  * Empty means
    - MR cannotbe merged.
    - Mr has merge conflicts (accoring to the API result).
"""

import requests
import os
import argparse
from collections import defaultdict
import sys
import logging

logging.basicConfig()
logger = logging.getLogger("EMPTY_MRS")
logger.setLevel(logging.INFO)


PROJECT_ID = os.environ.get("GITLAB_PROJECT_ID", None)
URL = os.environ.get("GITLAB_URL", None)

GITHUB_API_ENDPOINT = "/api/v4"
ISSUES_ENDPOINT = "/issues"
PROJECT_ENDPOINT = "/projects" + "/{project_id}"
MR_ENDPOINT = "/merge_requests"
MR_VERSION_ENDPOINT = "/{mr_iid}/versions"
TAGS_ENDPOINT = "/repository/tags"
PROJECT_TAGS_ENDPOINT = f"{PROJECT_ENDPOINT}" + f"{TAGS_ENDPOINT}"

CAN_BE_MERGED = "can_be_merged"
CANNOT_BE_MERGED = "cannot_be_merged"


def empty_mrs(url=URL, mr=None, headers=None):
    mr_versions = list()
    # if  CANNOT_BE_MERGED == mr["merge_status"] and mr["has_conflicts"]:
    url = url + GITHUB_API_ENDPOINT

    endpoint = ""
    if mr["project_id"]:
        endpoint = PROJECT_ENDPOINT.format(project_id=mr["project_id"])
    response = requests.get(url + endpoint + MR_ENDPOINT + MR_VERSION_ENDPOINT.format(mr_iid=mr["iid"]), headers=headers)
    if not response.status_code in [200, 201]:
        print(f"Received status code {response.status_code} with {response.text}")
        sys.exit

    json_response = response.json()
    logger.debug(json_response)


    for version in json_response:
        created_at = version.get("created_at", None)
        real_size = version.get("real_size", None)
        state = version.get("state", None)

        mr_versions.append({
            "created_at": created_at,
            "real_size": real_size,
            "state": state,
            "web_url": mr["web_url"],
        })

    return mr_versions