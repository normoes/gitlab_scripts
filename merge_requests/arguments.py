import argparse

from _version import __version__

def get_cli_arguments():

    parser = argparse.ArgumentParser(description='Create MR.', epilog="python create_mr.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url> --project <gitlab_project_id> --source-branch <gitlab_source_branch> --target-branch <gitlab_target_branch> --title <tite_of_mr> --assignee-id <gitlab_user_id> --remove-source-branch", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    parser.add_argument('-u', '--url', required=True, default="https://example.gitlab.com", help='Gitlab host/url/server.')
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

    return parser
