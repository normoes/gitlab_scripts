import requests
import os
import argparse
from collections import defaultdict
import sys
import json

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
    - python get_most_recent_tag.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url> --group <gitlab_group_id>
  * If the Private Token is set both ways, GITLAB_PRIVATE_TOKEN has precedence.
  * The gitlab group id can be given as environemnt variable GITLAB_GROUP_ID
  * The gitlab group id can be given as argument (-g, --group)
  * If the gitlab group id is set both ways, GITLAB_GROUP_ID has precedence.
  * The url can be given as argument (-u, --url)
  * The output can be limited to only the most recent tags of each repository (-l, --latest)
"""


PRIVATE_TOKEN = os.environ.get("GITLAB_PRIVATE_TOKEN", None)
GROUP_ID = os.environ.get("GITLAB_GROUP_ID", None)
URL = os.environ.get("GITLAB_URL", None)

GITHUB_API_ENDPOINT = "/api/v4"
ISSUES_ENDPOINT = "/issues"
PROJECT_ENDPOINT = "/projects" + "/{project_id}"
TAGS_ENDPOINT = "/repository/tags"
PROJECT_TAGS_ENDPOINT = f"{PROJECT_ENDPOINT}" + f"{TAGS_ENDPOINT}"

def get_most_recent_tags(url=URL, group_id=GROUP_ID, headers=None, latest_only=False):
    url = url + GITHUB_API_ENDPOINT

    group_endpoint = f"/groups/{group_id}/projects"
    print(f"{url + group_endpoint}")
    response = requests.get(url + f"{group_endpoint}", headers=headers)
    if not response.status_code == 200:
        print(f"Received status code {response.status_code} with {response.text}")
        sys.exit(1)
    projects = response.json()

    projects_tags = defaultdict(list)
    for project in projects:
        project_id = project.get("id", None)
        project_endpoint = PROJECT_TAGS_ENDPOINT.format(project_id=project_id)
        response = requests.get(url + project_endpoint, headers=headers)
        if not response.status_code == 200:
            print(f"Received status code {response.status_code} with {response.text}")
            sys.exit
        tags = response.json()
        for tag in tags:
            projects_tags[project.get("name", None)].append(tag.get("name", None))
            if latest_only:
                break
    return projects_tags


def main():
    parser = argparse.ArgumentParser(description='Get most recent tags in group repositories.', epilog="python get_most_recent_tag.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url> --group <gitlab_group_id> --latest", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-u', '--url', required=True, default="https://example.gitlab.com", help='Gitlab host/url/server.')
    parser.add_argument('-g', '--group', required=True, default="-1", help='Gitlab group id.')
    parser.add_argument('-t', '--token', nargs='?', help='Private Token to access gitlab API. If not given as argument, set GITLAB_PRIVATE_TOKEN.')
    # default=False is implied by action='store_true'
    parser.add_argument('-l', '--latest', action='store_true', help='Show most recent tag only.')
    args = parser.parse_args()


    if PRIVATE_TOKEN:
        private_token = PRIVATE_TOKEN
    else:
        private_token = args.token

    if GROUP_ID:
        group_id = GROUP_ID
    else:
        group_id = args.group

    latest_only = args.latest

    if URL:
        url = URL
    else:
        url = args.url

    headers = {"PRIVATE-TOKEN": private_token}

    tags = get_most_recent_tags(url=url, group_id=group_id, headers=headers, latest_only=latest_only)
    print(json.dumps(tags, indent=2))
    # for k, v in tags.items():
    #     print(k)
    #     print("  " +  "\n  ".join(t for t in v))


if __name__ == "__main__":
    sys.exit(main())
