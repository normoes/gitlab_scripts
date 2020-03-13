"""
Goal:
  * Get users.

How to:
  * Get help
    - python get_users.py -h
  * The Private Token can be given as environemnt variable GITLAB_PRIVATE_TOKEN
    - I read the password using pass (cli password manager)
    - GITLAB_PRIVATE_TOKEN=$(pass show work/CSS/gitlab/private_token) python get_users.py --user <user_name> --url <gitlab_url>
    - GITLAB_PRIVATE_TOKEN=$(pass show work/CSS/gitlab/private_token) python get_users.py --url <gitlab_url>
  * The Private Token can be given as argument (-t, --token)
    - python get_users.py --token $(pass show work/CSS/gitlab/private_token) --user <user_name> --url <gitlab_url>
    - python get_users.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url>
  * If the Private Token is set both ways, GITLAB_PRIVATE_TOKEN has precedence.
  * The user can be given as argument (-u, --user)
    - If no user is set, all users are returned.
  * The url can be given as argument (-l, --url)
"""

import sys
import logging
from json import JSONDecodeError

import requests


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

GITHUB_API_ENDPOINT = "/api/v4"
USERS_ENDPOINT = "/users"


def get_users(url=None, username="", headers=None):
    logger.debug(f"User '{username}'.")
    url = url + GITHUB_API_ENDPOINT
    user_ids = {}
    if username:
        # Get a specific gitlab user.
        complete_url = url + f"{USERS_ENDPOINT}?username={username}"
        response = requests.get(complete_url, headers=headers)
        if not response.status_code == 200:
            error = {
                "message": "Cannot get user '{user}'.",
                "reason": f"Received status code {response.status_code} with {response.text}.",
                "username": username,
            }
            logger.error(error)
            return {
                "error": error,
                "url": complete_url,
            }
        logger.debug(response.text)
        try:
            result = response.json()
            if result:
                user_ids[username] = result[0].get("id", None)
        except JSONDecodeError as e:
            error = {
                "message": "Is this JSON?.",
                "reason": f"Received status code {response.status_code} with {response.text}.",
                "error": str(e),
            }
            logger.error(error)
            return {
                "error": error,
                "url": complete_url,
            }
    else:
        # Get all gitlab users.
        complete_url = url + f"{USERS_ENDPOINT}"
        response = requests.get(complete_url, headers=headers)
        if not response.status_code == 200:
            error = {
                "message": "Cannot get users.",
                "reason": f"Received status code {response.status_code} with {response.text}.",
            }
            logger.error(error)
            return {
                "error": error,
                "url": complete_url,
            }
        logger.debug(response.text)
        try:
            users = response.json()
        except JSONDecodeError as e:
            error = {
                "message": "Is this JSON?.",
                "reason": f"Received status code {response.status_code} with {response.text}.",
                "error": str(e),
            }
            logger.error(error)
            return {
                "error": error,
                "url": complete_url,
            }
        for user in users:
            user_ids[user["username"]] = user.get("id", None)

    return user_ids


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Get users.", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-l",
        "--url",
        required=True,
        default="https://example.gitlab.com",
        help="Gitlab host/url/server.",
    )
    parser.add_argument(
        "-t",
        "--token",
        nargs="?",
        help="Private Token to access gitlab API. If not given as argument, set GITLAB_PRIVATE_TOKEN.",
    )
    parser.add_argument(
        "-u",
        "--username",
        default="",
        help="Gitlab username to get id for. If not set, all users' ids are listed.",
    )
    parser.add_argument("--debug", action="store_true", help="Show debug info.")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    private_token = args.token
    username = args.username
    url = args.url

    headers = {
        "PRIVATE-TOKEN": private_token,
        "Content-Type": "application/json",
    }

    users = get_users(url=url, username=username, headers=headers)
    print(users)


if __name__ == "__main__":
    sys.exit(main())
