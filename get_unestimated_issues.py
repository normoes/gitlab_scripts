import requests
import os
import argparse
from collections import defaultdict
import sys

"""
Goal:
  * Get unestimated issue over all gitlab projects assigned to a specific user

How to:
  * Get help
    - python get_unestimated_issues.py -h
  * The Private Token can be given as environemnt variable GITLAB_PRIVATE_TOKEN
    - I read the password using pass (cli password manager)
    - GITLAB_PRIVATE_TOKEN=$(pass show work/CSS/gitlab/private_token) python get_unestimated_issues.py --user <user_name> --url <gitlab_url>
  * The Private Token can be given as argument (-t, --token)
    - python get_unestimated_issues.py --token $(pass show work/CSS/gitlab/private_token) --user <user_name> --url <gitlab_url>
  * If the Private Token is set both ways, GITLAB_PRIVATE_TOKEN has precedence.
  * The user can be given as argument (-u, --user)
  * The url can be given as argument (-l, --url)

Optimizations:
  * Implement pagination and make sure to get ALL the projects and issues.
"""


PRIVATE_TOKEN = os.environ.get("GITLAB_PRIVATE_TOKEN", None)

GITHUB_API_ENDPOINT = "/api/v4"
USERS_ENDPOINT = "/users"
ISSUES_ENDPOINT = "/issues"

parser = argparse.ArgumentParser(description='Get unestimated gitlab issues for a user.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-l', '--url', required=True, default="https://example.gitlab.com", help='Gitlab host/url/server.')
parser.add_argument('-t', '--token', nargs='?', help='Private Token to access gitlab API. If not given as argument, set GITLAB_PRIVATE_TOKEN.')
parser.add_argument('-u', '--user', required=True, help='Gitlab username to get information for.')
args = parser.parse_args()

if not PRIVATE_TOKEN:
    PRIVATE_TOKEN = args.token
USER = args.user
URL = args.url + GITHUB_API_ENDPOINT

headers = {"PRIVATE-TOKEN": PRIVATE_TOKEN}

def get_unestimated_issues():
    # get gitlab user id
    response = requests.get(URL + f"{USERS_ENDPOINT}?username={USER}", headers=headers)
    if not response.status_code == 200:
        print(f"Received status code {response.status_code} with {response.text}")
        sys.exit
    user_id = response.json()[0].get("id", None)

    # get all users' issues
    response = requests.get(URL + f"{ISSUES_ENDPOINT}?scope=assigned_to_me&assignee_id={user_id}&state=opened", headers=headers)
    if not response.status_code == 200:
        print(f"Received status code {response.status_code} with {response.text}")
        sys.exit
    issues = response.json()
    issues_not_estimated = defaultdict(list)
    for issue in issues:
        timestats = issue.get("time_stats", None)
        if timestats:
            estimated = timestats.get("time_estimate", None)
            # only collect unestimated issues, add some information
            if not estimated:
                issues_not_estimated[issue.get("id", None)].append(("project_id", str(issue.get("project_id", None))))
                issues_not_estimated[issue.get("id", None)].append(("title", issue.get("title", None)))
                issues_not_estimated[issue.get("id", None)].append(("web_url", issue.get("web_url", None)))
                issues_not_estimated[issue.get("id", None)].append(("labels", ", ".join(issue.get("labels", None))))
                issues_not_estimated[issue.get("id", None)].append(("time estimated [seconds]", str(estimated)))
                issues_not_estimated[issue.get("id", None)].append(("total_time_spent [seconds]", str(timestats.get("total_time_spent", None))))
    return issues_not_estimated


if __name__ == "__main__":
    issues_not_estimated = get_unestimated_issues()
    for k, v in issues_not_estimated.items():
        print(k)
        print("  " +  "\n  ".join(t[0] + ": " + t[1] for t in v))
