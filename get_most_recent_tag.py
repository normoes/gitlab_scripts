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

* '--latest' only returns the latest tag.
* without '--latets':
    - returns the last 5 tags.
    - The number of tags returned can be modified with '--amount'
    - '--amount -1' returns all tags found for the project.
"""


import os
from collections import defaultdict
import sys
import json
import logging
from threading import Thread
from queue import Queue
from urllib.parse import quote_plus

import requests
from requests.exceptions import (
    ConnectionError as RequestsConnectionError,
    ReadTimeout,
    Timeout,
)

logging.basicConfig()
logger = logging.getLogger("GitlabTags")
logger.setLevel(logging.INFO)

PRIVATE_TOKEN = os.environ.get("GITLAB_PRIVATE_TOKEN", None)
GROUP_ID = os.environ.get("GITLAB_GROUP_ID", None)
PROJECT_ID = os.environ.get("PROJECT_GROUP_ID", None)
URL = os.environ.get("GITLAB_URL", None)

GITHUB_API_ENDPOINT = "/api/v4"
ISSUES_ENDPOINT = "/issues"
PROJECT_ENDPOINT = "/projects" + "/{project_id}"
GROUP_ENDPOINT = "/groups" + "/{group_id}"
TAGS_ENDPOINT = "/repository/tags"
PROJECT_TAGS_ENDPOINT = f"{PROJECT_ENDPOINT}" + f"{TAGS_ENDPOINT}"

projects_tags_queue = Queue()

NUMBER_OF_TAGS_TO_SHOW = 5


def get_tags(
    url=URL,
    project=None,
    headers=None,
    latest_only=False,
    number_of_tags=NUMBER_OF_TAGS_TO_SHOW,
):
    """Get tags from a repository.

    The API request returns an ordered list of tags.
    The most recent tag is the first one in the list.

    :param latest_only: Only return the most recent tag.
    :param number_of_tags: Number of tags to show. Not considered with 'latest_only'.
    """

    project_id = project.get("id", None)
    project_name = project.get("name", None)
    logger.debug(project)
    project_endpoint = PROJECT_TAGS_ENDPOINT.format(
        project_id=quote_plus(str(project_id))
    )
    logger.debug(url + project_endpoint)
    response = requests.get(url + project_endpoint, headers=headers)
    if not response.status_code == 200:
        print(
            f"Project '{project_name}' received status code '{response.status_code}' with '{response.text}'."
        )
        sys.exit(1)
    tags = response.json()
    project_tags = defaultdict(list)
    count = 0
    for tag in tags:
        project_tags[project_name].append(tag.get("name", None))
        if latest_only:
            break
        else:
            count += 1
            if number_of_tags > 0 and number_of_tags - count == 0:
                break

    projects_tags_queue.put(project_tags)

    return latest_only


def get_group_tags(
    url=URL,
    group_id=GROUP_ID,
    project_id=PROJECT_ID,
    headers=None,
    latest_only=False,
    number_of_tags=NUMBER_OF_TAGS_TO_SHOW,
):
    url = url + GITHUB_API_ENDPOINT

    if group_id:
        group_endpoint = (
            GROUP_ENDPOINT.format(group_id=quote_plus(str(group_id))) + "/projects"
        )
        logger.debug(f"GROUP URL: {url+group_endpoint}")
    elif project_id:
        project_endpoint = PROJECT_TAGS_ENDPOINT.format(
            project_id=quote_plus(str(project_id))
        )
        logger.debug(f"PROJECT URL: {url+project_endpoint}")

    response = None
    projects = []
    if group_id:
        try:
            response = requests.get(url + f"{group_endpoint}", headers=headers)
            projects = response.json()
            if not response.status_code == 200:
                print(
                    f"Received status code {response.status_code} with {response.text}"
                )
                sys.exit(1)
        except (RequestsConnectionError, ReadTimeout, Timeout) as e:
            # TODO Add logging.
            # TODO Add error key and message.
            print(f"Some error occurred: '{str(e)}'.")
    elif project_id:
        projects = [{"id": project_id, "name": project_id,}]

    threads = []

    for project in projects:
        # if not latest_only:
        thread = Thread(
            target=get_tags,
            kwargs={
                "url": url,
                "project": project,
                "headers": headers,
                "latest_only": latest_only,
                "number_of_tags": number_of_tags,
            },
        )
        thread.daemon = True
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()  # wait for end of threads

    projects_tags = defaultdict(list)
    while not projects_tags_queue.empty():
        # project_tags = projects_tags_queue.get()
        # projects_tags[next(iter(project_tags))] = project[next(iter(project_tags))]
        project_tags = projects_tags_queue.get()
        if not projects_tags:
            projects_tags = project_tags
        else:
            projects_tags.update(project_tags)
        projects_tags_queue.task_done()

    return projects_tags
    # return sorted(projects_tags.items())


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Get most recent tags in group repositories.",
        epilog="python get_most_recent_tag.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url> --group <gitlab_group_id> --latest",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-u",
        "--url",
        required=True,
        default="https://example.gitlab.com",
        help="Gitlab host/url/server.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-g", "--group", default="", help="Gitlab group id.")
    group.add_argument("-p", "--project", default="", help="Gitlab project id.")
    parser.add_argument(
        "-t",
        "--token",
        nargs="?",
        help="Private Token to access gitlab API. If not given as argument, set GITLAB_PRIVATE_TOKEN.",
    )
    parser.add_argument(
        "--amount",
        type=int,
        default=NUMBER_OF_TAGS_TO_SHOW,
        help="Number of tags to show. '-1' returns all tags.",
    )
    # default=False is implied by action='store_true'
    parser.add_argument(
        "-l", "--latest", action="store_true", help="Show most recent tag only."
    )
    parser.add_argument("--debug", action="store_true", help="Show debug info.")

    args = parser.parse_args()

    debug = args.debug
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.debug(args.url)
    url = args.url
    logger.debug(url)
    private_token = args.token
    group_id = args.group
    project_id = args.project
    latest_only = args.latest
    number_of_tags = args.amount

    headers = {"PRIVATE-TOKEN": private_token}

    tags = {}
    if group_id:
        tags = get_group_tags(
            url=url,
            group_id=group_id,
            headers=headers,
            latest_only=latest_only,
            number_of_tags=number_of_tags,
        )
    elif project_id:
        tags = get_group_tags(
            url=url,
            project_id=project_id,
            headers=headers,
            latest_only=latest_only,
            number_of_tags=number_of_tags,
        )

    print(json.dumps(tags, indent=2))


if __name__ == "__main__":
    sys.exit(main())
