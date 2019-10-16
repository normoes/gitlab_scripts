import requests
import os
import argparse
from collections import defaultdict
import sys
import logging

"""
Goal:
  * Create MR.

How to:
  * Get help
    - python create_mr.py -h
  * The Private Token can be given as environemnt variable GITLAB_PRIVATE_TOKEN
    - I read the password using pass (cli password manager)
    - GITLAB_PRIVATE_TOKEN=$(pass show work/CSS/gitlab/private_token) python create.py --url <gitlab_url> --project <gitlab_project_id> --source-branch <gitlab_source_branch> --target-branch <gitlab_target_branch> --title <tite_of_mr> --assignee-id <gitlab_user_id> --remove-source-branch
  * The Private Token can be given as argument (-t, --token)
    - python get_most_recent_tag.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url> --project <gitlab_project_id> --source-branch <gitlab_source_branch> --target-branch <gitlab_target_branch> --title <tite_of_mr> --assignee-id <gitlab_user_id> --remove-source-branch
  * If the Private Token is set both ways, GITLAB_PRIVATE_TOKEN has precedence.
  * The gitlab project id can be given as environemnt variable GITLAB_PROJECT_ID
  * The gitlab project id can be given as argument (-p, --project)
  * If the gitlab project id is set both ways, GITLAB_PROJECT_ID has precedence.
  * The url can be given as argument (-u, --url)
"""

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


PRIVATE_TOKEN = os.environ.get("GITLAB_PRIVATE_TOKEN", None)
PROJECT_ID = os.environ.get("GITLAB_PROJECT_ID", None)
SOURCE_BRANCH = os.environ.get("GITLAB_SOURCE_BRANCH", None)
TARGET_BRANCH = os.environ.get("GITLAB_TARGET_BRANCH", None)
MR_TITLE = os.environ.get("GITLAB_MR_TITLE", None)
ASSIGNEE_ID  = os.environ.get("GITLAB_ASSIGNEE_ID", None)
URL = os.environ.get("GITLAB_URL", None)

GITHUB_API_ENDPOINT = "/api/v4"
ISSUES_ENDPOINT = "/issues"
PROJECT_ENDPOINT = "/projects" + "/{project_id}"
MR_ENDPOINT = "/merge_requests"
TAGS_ENDPOINT = "/repository/tags"
PROJECT_TAGS_ENDPOINT = f"{PROJECT_ENDPOINT}" + f"{TAGS_ENDPOINT}"

def create_mr(url=URL, project_id=PROJECT_ID, source_branch=SOURCE_BRANCH, target_branch=TARGET_BRANCH, title=MR_TITLE, assignee_id=ASSIGNEE_ID, headers=None, remove_source_branch=False):
    url = url + GITHUB_API_ENDPOINT

    data = {
        "id": project_id,
        "source_branch": source_branch,
        "target_branch": target_branch,
        "remove_source_branch": remove_source_branch,
        "title": f"WIP: {title}",
        "assignee_id": assignee_id,
    }

    project_endpoint = PROJECT_ENDPOINT.format(project_id=project_id)
    response = requests.post(url + project_endpoint + MR_ENDPOINT, json=data, headers=headers)
    if not response.status_code in [200, 201]:
        print(f"Received status code {response.status_code} with {response.text}")
        sys.exit

    json_response = response.json()
    logger.debug(json_response)

    merge_status = json_response.get("merge_status", None)
    web_url = json_response.get("web_url", None)
    user_info =  json_response.get("user", None)
    assignee_can_merge = None
    if user_info:
        assignee_can_merge = user_info.get("can_merge", None)

    return {
        "assignee_can_merge": assignee_can_merge,
        "merge_status": merge_status,
        "web_url": web_url,
    }



def main():
    parser = argparse.ArgumentParser(description='Create MR.', epilog="python create_mr.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url> --project <gitlab_project_id> --source-branch <gitlab_source_branch> --target-branch <gitlab_target_branch> --title <tite_of_mr> --assignee-id <gitlab_user_id> --remove-source-branch", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-u', '--url', required=True, default="https://example.gitlab.com", help='Gitlab host/url/server.')
    parser.add_argument('-p', '--project', required=True, default="-1", help='Gitlab project id.')
    parser.add_argument('-t', '--token', nargs='?', help='Private Token to access gitlab API. If not given as argument, set GITLAB_PRIVATE_TOKEN.')
    parser.add_argument('--source-branch', required=True, default="staging", help='Source branch.')
    parser.add_argument('--target-branch', required=True, default="master", help='Target branch.')
    parser.add_argument('--title', required=True, default="MR title.", help='Merge request title.')
    parser.add_argument('--assignee-id', required=True, default=-1, help='Gitlab user id of assignee.')
    # default=False is implied by action='store_true'
    parser.add_argument('--remove-source-branch', action='store_true', help='Remove the source branch after merging.')
    parser.add_argument(
        "--debug", action='store_true',  help="Show debug info."
    )

    args = parser.parse_args()

    if args.debug:
         logger.setLevel(logging.DEBUG)
    else:
         logger.setLevel(logging.INFO)

    if PRIVATE_TOKEN:
        private_token = PRIVATE_TOKEN
    else:
        private_token = args.token

    if PROJECT_ID:
        project_id = PROJECT_ID
    else:
        project_id = args.project

    if SOURCE_BRANCH:
        source_branch = SOURCE_BRANCH
    else:
        source_branch = args.source_branch

    if TARGET_BRANCH:
        target_branch = TARGET_BRANCH
    else:
        target_branch = args.target_branch

    if MR_TITLE:
        title = MR_TITLE
    else:
        title = args.title

    if ASSIGNEE_ID:
        assignee_id = ASSIGNEEE_ID
    else:
        assignee_id = args.assignee_id

    if URL:
        url = URL
    else:
        url = args.url

    remove_source_branch = args.remove_source_branch

    headers = {
        "PRIVATE-TOKEN": private_token,
        "Content-Type": "application/json",
    }

    created_mr = create_mr(url=url, project_id=project_id, source_branch=source_branch, target_branch=target_branch, title=title, assignee_id=assignee_id, headers=headers, remove_source_branch=remove_source_branch)
    print(created_mr)
    # for k, v in tags.items():
    #     print(k)
    #     print("  " +  "\n  ".join(t for t in v))


if __name__ == "__main__":
    sys.exit(main())
