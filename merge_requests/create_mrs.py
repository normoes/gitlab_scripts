import sys
import logging

from create_mr import create_mr
import environment_variables

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_mrs(
    url=environment_variables.URL,
    project_ids=environment_variables.PROJECT_ID,
    source_branch=environment_variables.SOURCE_BRANCH,
    target_branch=environment_variables.TARGET_BRANCH,
    title=environment_variables.MR_TITLE,
    description=environment_variables.MR_DESCRIPTION,
    assignee_id=environment_variables.ASSIGNEE_ID,
    milestone_id=environment_variables.MILESTONE_ID,
    headers=None,
    remove_source_branch=False,
    only_check_differences=False,
):
    mrs = []
    try:
        for project_id in project_ids:
            logger.info(f"Trying to create MR for project '{project_id}'.")
            mrs.append(
                create_mr(
                    url=url,
                    project_id=project_id,
                    source_branch=source_branch,
                    target_branch=target_branch,
                    title=title,
                    description=description,
                    assignee_id=assignee_id,
                    milestone_id=milestone_id,
                    remove_source_branch=remove_source_branch,
                    only_check_differences=only_check_differences,
                    headers=headers,
                )
            )
    except (Exception) as e:
        logger.error(f"Error: '{str(e)}'.")

    return mrs


def main():
    import arguments
    import json

    parser = arguments.get_cli_arguments()
    parser.add_argument(
        "-p",
        "--projects",
        required=True,
        nargs="+",
        help="Gitlab project ids. Pass several divided by whitespace.",
    )

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    private_token = args.token
    project_ids = args.projects
    source_branch = args.source_branch
    target_branch = args.target_branch
    title = args.title
    description = args.description
    assignee_id = args.assignee_id
    milestone_id = args.milestone_id
    url = args.url
    remove_source_branch = args.remove_source_branch
    only_check_differences = args.only_check_diffs

    headers = {
        "PRIVATE-TOKEN": private_token,
        "Content-Type": "application/json",
    }

    created_mrs = create_mrs(
        url=url,
        project_ids=project_ids,
        source_branch=source_branch,
        target_branch=target_branch,
        title=title,
        description=description,
        assignee_id=assignee_id,
        milestone_id=milestone_id,
        headers=headers,
        remove_source_branch=remove_source_branch,
        only_check_differences=only_check_differences,
    )
    logger.debug(created_mrs)
    for mr in created_mrs:
        print(json.dumps(mr))


if __name__ == "__main__":
    sys.exit(main())
