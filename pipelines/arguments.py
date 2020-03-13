import argparse

from _version import __version__


def get_cli_arguments():

    parser = argparse.ArgumentParser(
        description="Create Pipeline.",
        epilog="python create_pipeline.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url> --project <gitlab_project_id> --reference <branch_tag_or_other_reference>",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    parser.add_argument(
        "-u",
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
    parser.add_argument("--reference", required=True, help="Target branch.")
    # default=False is implied by action='store_true'
    parser.add_argument("--debug", action="store_true", help="Show debug info.")

    return parser
