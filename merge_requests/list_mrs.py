"""
Goal:
  * List open MR.

Todos:
  * Make project and group arguments exclusive.

How to:
  * Get help
    - python list_mrs.py -h
  * The Private Token can be given as environemnt variable GITLAB_PRIVATE_TOKEN
    - I read the password using pass (cli password manager)
    - GITLAB_PRIVATE_TOKEN=$(pass show work/CSS/gitlab/private_token) python list_mrs.py --url <gitlab_url> --group <group_id> --project=<project_id>
  * The Private Token can be given as argument (-t, --token)
    - python list_mrs.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url> --group <group_id> --project <gitlab_project_id>
  * If the Private Token is set both ways, GITLAB_PRIVATE_TOKEN has precedence.
  * The gitlab project id can be given as environemnt variable GITLAB_PROJECT_ID
  * The gitlab project id can be given as argument (-p, --project)
  * If the gitlab project id is set both ways, GITLAB_PROJECT_ID has precedence.
  * The url can be given as argument (-u, --url)

Attention:
  * For now, to make '--group <group_id>' working set '--project_id=""'.
"""

import requests
import os
import argparse
from collections import defaultdict
import sys
import logging

from get_empty_mrs import empty_mrs

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


STATE_DEFAULT = "all"

PRIVATE_TOKEN = os.environ.get("GITLAB_PRIVATE_TOKEN", None)
PROJECT_ID = os.environ.get("GITLAB_PROJECT_ID", None)
GROUP_ID = os.environ.get("GITLAB_GROUP_ID", None)
URL = os.environ.get("GITLAB_URL", None)

GITHUB_API_ENDPOINT = "/api/v4"
ISSUES_ENDPOINT = "/issues"
PROJECT_ENDPOINT = "/projects" + "/{project_id}"
GROUP_ENDPOINT = "/groups" + "/{group_id}"
MR_ENDPOINT = "/merge_requests"
TAGS_ENDPOINT = "/repository/tags"
PROJECT_TAGS_ENDPOINT = f"{PROJECT_ENDPOINT}" + f"{TAGS_ENDPOINT}"

CAN_BE_MERGED = "can_be_merged"
CANNOT_BE_MERGED = "cannot_be_merged"

def list_mrs(url=URL, project_id=PROJECT_ID, group_id=GROUP_ID, state=STATE_DEFAULT, headers=None):
    url = url + GITHUB_API_ENDPOINT

    endpoint = ""
    if project_id:
        endpoint = PROJECT_ENDPOINT.format(project_id=project_id)
    elif group_id:
        endpoint = GROUP_ENDPOINT.format(group_id=group_id)
    response = requests.get(url + endpoint + MR_ENDPOINT + f"?state={state}", headers=headers)
    if not response.status_code in [200, 201]:
        print(f"Received status code {response.status_code} with {response.text}")
        sys.exit

    json_response = response.json()
    logger.debug(json_response)

    mrs = list()
    for mr in json_response:
        iid = mr.get("iid", None)
        merge_status = mr.get("merge_status", None)
        has_conflicts = mr.get("has_conflicts", None)
        web_url = mr.get("web_url", None)
        project_id = mr.get("project_id", None)
        # user_info =  mr.get("user", None)
        # assignee_can_merge = None
        # if user_info:
        #     assignee_can_merge = user_info.get("can_merge", None)

        mrs.append({
            "iid": iid,
        #     "assignee_can_merge": assignee_can_merge,
            "merge_status": merge_status,
            "has_conflicts": has_conflicts,
            "web_url": web_url,
            "project_id": project_id,
            "group_id": group_id,
        #     "assignee_id": assignee_id,
        #     "source_branch": source_branch,
        #     "target_branch": target_branch,
        })

    return mrs


def main():
    from _version import __version__

    parser = argparse.ArgumentParser(description='List open MR.', epilog="python list_mrs.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url> --project <gitlab_project_id>", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    parser.add_argument('-u', '--url', required=True, default="https://example.gitlab.com", help='Gitlab host/url/server.')
    parser.add_argument('-p', '--project', required=True, default="-1", help='Gitlab project id.')
    parser.add_argument('-g', '--group', required=True, default="-1", help='Gitlab group id.')
    parser.add_argument('-s', '--state', default=STATE_DEFAULT, help='State of MRs to be listed.')
    parser.add_argument('-t', '--token', nargs='?', help='Private Token to access gitlab API. If not given as argument, set GITLAB_PRIVATE_TOKEN.')
    parser.add_argument(
        "--debug", action='store_true',  help="Show debug info."
    )

    args = parser.parse_args()

    if args.debug:
         logger.setLevel(logging.DEBUG)
         logging.getLogger("EMPTY_MRS").setLevel(logging.DEBUG)
    else:
         logger.setLevel(logging.INFO)
         logging.getLogger("EMPTY_MRS").setLevel(logging.INFO)

    private_token = args.token
    project_id = args.project
    group_id = args.group
    state = args.state
    url = args.url

    headers = {
        "PRIVATE-TOKEN": private_token,
        "Content-Type": "application/json",
    }

    listed_mrs = list_mrs(url=url, project_id=project_id, group_id=group_id, state=state, headers=headers)
    print(*listed_mrs, sep="\n")
    # for k, v in tags.items():
    #     print(k)
    #     print("  " +  "\n  ".join(t for t in v))

    for mr in listed_mrs:
        # Get not mergeable MRs with conflicts.
        # This seems to contains empty MRs.
        result = empty_mrs(url=url, mr=mr, headers=headers)
        if result:
            print(result)

if __name__ == "__main__":
    sys.exit(main())
