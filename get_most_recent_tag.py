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


import logging
import os
import argparse
from collections import defaultdict
import sys
import json
from threading import Thread
from queue import Queue

import requests
from requests.exceptions import (
    ConnectionError as RequestsConnectionError,
    ReadTimeout,
    Timeout,
)

PRIVATE_TOKEN = os.environ.get("GITLAB_PRIVATE_TOKEN", None)
GROUP_ID = os.environ.get("GITLAB_GROUP_ID", None)
URL = os.environ.get("GITLAB_URL", None)

GITHUB_API_ENDPOINT = "/api/v4"
ISSUES_ENDPOINT = "/issues"
PROJECT_ENDPOINT = "/projects" + "/{project_id}"
TAGS_ENDPOINT = "/repository/tags"
PROJECT_TAGS_ENDPOINT = f"{PROJECT_ENDPOINT}" + f"{TAGS_ENDPOINT}"

projects_tags_queue = Queue()

def get_tags(url=URL, project=None, headers=None, latest_only=False):
    """Get tags from a repository.

    The API request returns an ordered list of tags.
    The most recent tag is the first one in the list.

    :param latest_only: Only return the most recent tag.
    """

    project_id = project.get("id", None)
    project_name = project.get("name", None)
    project_endpoint = PROJECT_TAGS_ENDPOINT.format(project_id=project_id)
    response = requests.get(url + project_endpoint, headers=headers)
    if not response.status_code == 200:
        print(f"Project '{project_name}' received status code '{response.status_code}' with '{response.text}'.")
        sys.exit(1)
    tags = response.json()
    project_tags = defaultdict(list)
    for tag in tags:
        project_tags[project_name].append(tag.get("name", None))
        if latest_only:
            break

    projects_tags_queue.put(project_tags)

    return latest_only

def get_project_tags(url=URL, group_id=GROUP_ID, headers=None, latest_only=False):
    url = url + GITHUB_API_ENDPOINT

    group_endpoint = f"/groups/{group_id}/projects"
    print(f"{url + group_endpoint}")
    try:
        response = requests.get(url + f"{group_endpoint}", headers=headers)
        if not response.status_code == 200:
            print(f"Received status code {response.status_code} with {response.text}")
            sys.exit(1)
    except (RequestsConnectionError, ReadTimeout, Timeout) as e:
        # TODO Add logging.
        # TODO Add error key and message.
        print(f"Some error occurred: '{str(e)}'.")

    projects = response.json()

    projects_tags = defaultdict(list)

    if not latest_only:
        threads = []

    for project in projects:
        if not latest_only:
            thread = Thread(target=get_tags, kwargs={"url": url, "project": project, "headers": headers, "latest_only": latest_only, })
            thread.daemon = True
            thread.start()
            threads.append(thread)
        else:
            if get_tags(project=project, headers=headers, latest_only=latest_only):
                break

    if not latest_only:
        for thread in threads:
            thread.join()  # wait for end of threads

    while not projects_tags_queue.empty():
        # project_tags = projects_tags_queue.get()
        # projects_tags[next(iter(project_tags))] = project[next(iter(project_tags))]
        project_tags = projects_tags_queue.get()
        if not projects_tags:
            projects_tags = project_tags
        else:
            projects_tags.update(project_tags)
        projects_tags_queue.task_done()

    return sorted(projects_tags.items())


def main():
    parser = argparse.ArgumentParser(description='Get most recent tags in group repositories.', epilog="python get_most_recent_tag.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url> --group <gitlab_group_id> --latest", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-u', '--url', required=True, default="https://example.gitlab.com", help='Gitlab host/url/server.')
    parser.add_argument('-g', '--group', required=True, default="-1", help='Gitlab group id.')
    parser.add_argument('-t', '--token', nargs='?', help='Private Token to access gitlab API. If not given as argument, set GITLAB_PRIVATE_TOKEN.')
    # default=False is implied by action='store_true'
    parser.add_argument('-l', '--latest', action='store_true', help='Show most recent tag only.')
    args = parser.parse_args()

    url = args.url
    private_token = args.token
    group_id = args.group
    latest_only = args.latest

    headers = {"PRIVATE-TOKEN": private_token}

    tags = get_project_tags(url=url, group_id=group_id, headers=headers, latest_only=latest_only)
    print(json.dumps(tags, indent=2))


if __name__ == "__main__":
    sys.exit(main())
