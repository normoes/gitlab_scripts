import requests
import os
import argparse
from collections import defaultdict
import sys

"""
Goal:
  * Get most recent tags of the repositories within a group.

How to:
  * Get help
    - python get_most_recent_tag.py -h
  * The Private Token can be given as environemnt variable GITLAB_PRIVATE_TOKEN
    - I read the password using pass (cli password manager)
    - GITLAB_PRIVATE_TOKEN=$(pass show work/CSS/gitlab/private_token) python get_most_recent_tag.py --url <gitlab_url> --group <gitlab_group_id>
  * The Private Token can be given as argument (-t, --token)
    - python get_most_recent_tag.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url> -- group <gitlab_group_id>
  * If the Private Token is set both ways, GITLAB_PRIVATE_TOKEN has precedence.
  * The gitlab group id can be given as environemnt variable GITLAB_GROUP_ID
  * The gitlab group id can be given as argument (-g, --group)
  * If the gitlab group id is set both ways, GITLAB_GROUP_ID has precedence.
"""


PRIVATE_TOKEN = os.environ.get("GITLAB_PRIVATE_TOKEN", None)
GROUP_ID = os.environ.get("GITLAB_GROUP_ID", None)

GITHUB_API_ENDPOINT = "/api/v4"
ISSUES_ENDPOINT = "/issues"
PROJECT_ENDPOINT = "/projects" + "/{project_id}"
TAGS_ENDPOINT = "/repository/tags"
PROJECT_TAGS_ENDPOINT = f"{PROJECT_ENDPOINT}" + f"{TAGS_ENDPOINT}"

parser = argparse.ArgumentParser(description='Get most recent tags in group repositories.')
parser.add_argument('-l', '--url', required=True, default="https://example.gitlab.com", help='Gitlab host/url/server.')
parser.add_argument('-g', '--group', required=True, default="1", help='Gitlab group id.')
parser.add_argument('-t', '--token', nargs='?', help='Private Token to access gitlab API. If not given as argument, set GITLAB_PRIVATE_TOKEN.')
args = parser.parse_args()

if not PRIVATE_TOKEN:
    PRIVATE_TOKEN = args.token
if not GROUP_ID:
    GROUP_ID = args.group
URL = args.url + GITHUB_API_ENDPOINT

headers = {"PRIVATE-TOKEN": PRIVATE_TOKEN}

def get_most_recent_tags(group_id=-1):
    group_endpoint = f"/groups/{group_id}/projects"
    response = requests.get(URL + f"{group_endpoint}", headers=headers)
    if not response.status_code == 200:
        print(f"Received status code {response.status_code} with {response.text}")
        sys.exit
    projects = response.json()

    projects_tags = defaultdict(list)
    for project in projects:
        project_id = project.get("id", None)
        project_endpoint = PROJECT_TAGS_ENDPOINT.format(project_id=project_id)
        response = requests.get(URL + project_endpoint, headers=headers)
        if not response.status_code == 200:
            print(f"Received status code {response.status_code} with {response.text}")
            sys.exit
        tags = response.json()
        for tag in tags:
            projects_tags[project.get("name", None)].append(tag.get("name", None))
    return projects_tags

if __name__ == "__main__":
    tags = get_most_recent_tags(group_id=GROUP_ID)
    for k, v in tags.items():
        print(k)
        print("  " +  "\n  ".join(t for t in v))