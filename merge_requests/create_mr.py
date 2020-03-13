"""
Goal:
  * Create MR.

How to:
  * Get help
    - python create_mr.py -h
  * The Private Token can be given as environemnt variable GITLAB_PRIVATE_TOKEN
    - I read the password using pass (cli password manager)
    - GITLAB_PRIVATE_TOKEN=$(pass show work/CSS/gitlab/private_token) python create_mr.py --url <gitlab_url> --source-branch <gitlab_source_branch> --target-branch <gitlab_target_branch> --title <tite_of_mr> --assignee-id <gitlab_user_id> --remove-source-branch --project <gitlab_project_id>
  * The Private Token can be given as argument (-t, --token)
    - python create_mr.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url> --source-branch <gitlab_source_branch> --target-branch <gitlab_target_branch> --title <tite_of_mr> --assignee-id <gitlab_user_id> --remove-source-branch --project <gitlab_project_id>
  * If the Private Token is set both ways, GITLAB_PRIVATE_TOKEN has precedence.
  * The gitlab project id can be given as environemnt variable GITLAB_PROJECT_ID
  * The gitlab project id can be given as argument (-p, --project)
  * If the gitlab project id is set both ways, GITLAB_PROJECT_ID has precedence.
  * The url can be given as argument (-u, --url)
"""

import requests
import sys
import logging
from urllib.parse import quote_plus

import environment_variables

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


GITHUB_API_ENDPOINT = "/api/v4"
ISSUES_ENDPOINT = "/issues"
PROJECT_ENDPOINT = "/projects" + "/{project_id}"
MR_ENDPOINT = "/merge_requests"
TAGS_ENDPOINT = "/repository/tags"
PROJECT_TAGS_ENDPOINT = f"{PROJECT_ENDPOINT}" + f"{TAGS_ENDPOINT}"

CAN_BE_MERGED = "can_be_merged"
CANNOT_BE_MERGED = "cannot_be_merged"


def create_mr(
    url=environment_variables.URL,
    project_id=environment_variables.PROJECT_ID,
    source_branch=environment_variables.SOURCE_BRANCH,
    target_branch=environment_variables.TARGET_BRANCH,
    title=environment_variables.MR_TITLE,
    assignee_id=environment_variables.ASSIGNEE_ID,
    headers=None,
    remove_source_branch=False,
):
    url = url + GITHUB_API_ENDPOINT

    data = {
        "id": project_id,
        "source_branch": source_branch,
        "target_branch": target_branch,
        "remove_source_branch": remove_source_branch,
        "title": f"{title}",
        "assignee_id": assignee_id,
    }

    project_endpoint = PROJECT_ENDPOINT.format(project_id=quote_plus(project_id))
    # Compare branches before creating the merge request.
    # Using '&straight=true' (default is 'false') to show 'diffs' in response.
    # Using 'false' returned empty 'diffs'.
    complete_url = (
        url
        + project_endpoint
        + f"/repository/compare?from={source_branch}&to={target_branch}&straight=true"
    )
    response = requests.get(url=complete_url, headers=headers)
    if response.status_code not in [200, 201]:
        error = {
            "message": CANNOT_BE_MERGED,
            "reason": f"Received status code {response.status_code} with {response.text}.",
            "project_id": project_id,
        }
        logger.error(error)
        return {
            "error": error,
            "project_id": project_id,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "url": complete_url,
        }

    json_response = response.json()

    diffs = json_response["diffs"]

    if not diffs:
        error = {
            "message": CANNOT_BE_MERGED,
            "reason": "No changes detected. Not creating empty MR.",
            "project_id": project_id,
        }
        logger.error(error)
        return {
            "error": error,
            "project_id": project_id,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "url": complete_url,
        }

    complete_url = url + project_endpoint + MR_ENDPOINT
    response = requests.post(url=complete_url, json=data, headers=headers)
    if response.status_code not in [200, 201]:
        error = {
            "message": CANNOT_BE_MERGED,
            "reason": f"Received status code {response.status_code} with {response.text}.",
            "project_id": project_id,
        }
        logger.error(error)
        return {
            "error": error,
            "project_id": project_id,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "url": complete_url,
        }

    json_response = response.json()
    logger.debug(json_response)

    iid = json_response.get("iid", None)
    merge_status = json_response.get("merge_status", None)
    has_conflicts = json_response.get("has_conflicts", None)
    web_url = json_response.get("web_url", None)
    user_info = json_response.get("user", None)
    assignee_can_merge = None
    if user_info:
        assignee_can_merge = user_info.get("can_merge", None)

    return {
        "iid": iid,
        "assignee_can_merge": assignee_can_merge,
        "merge_status": merge_status,
        "has_conflicts": has_conflicts,
        "web_url": web_url,
        "project_id": project_id,
        "assignee_id": assignee_id,
        "source_branch": source_branch,
        "target_branch": target_branch,
    }


def main():
    import arguments

    parser = arguments.get_cli_arguments()
    parser.add_argument(
        "-p", "--project", required=True, default="-1", help="Gitlab project id."
    )

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    private_token = args.token
    project_id = args.project
    source_branch = args.source_branch
    target_branch = args.target_branch
    title = args.title
    assignee_id = args.assignee_id
    url = args.url
    remove_source_branch = args.remove_source_branch

    headers = {
        "PRIVATE-TOKEN": private_token,
        "Content-Type": "application/json",
    }

    created_mr = create_mr(
        url=url,
        project_id=project_id,
        source_branch=source_branch,
        target_branch=target_branch,
        title=title,
        assignee_id=assignee_id,
        headers=headers,
        remove_source_branch=remove_source_branch,
    )
    print(created_mr)


if __name__ == "__main__":
    sys.exit(main())
