import sys
import logging
import json

from create_pipeline import create_pipeline
import environment_variables

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_pipelines(url=environment_variables.URL, project_ids=environment_variables.PROJECT_ID, reference=environment_variables.REFERENCE, headers=None):
    pipelines = []
    try:
        for project_id in project_ids:
            logger.info(f"Trying to create pipeline for project '{project_id}'.")
            pipelines.append(create_pipeline(url=url, project_id=project_id, reference=reference, headers=headers))
    except (Exception) as e:
        logger.error(f"Error: str(e).")

    return pipelines


def main():
    import arguments

    parser = arguments.get_cli_arguments()
    parser.add_argument('-p', '--projects', required=True, nargs="+", help='Gitlab project ids. Pass several divided by whitespace.')

    args = parser.parse_args()

    if args.debug:
         logger.setLevel(logging.DEBUG)
    else:
         logger.setLevel(logging.INFO)

    private_token = args.token
    project_ids = args.projects
    reference = args.reference
    url = args.url

    headers = {
        "PRIVATE-TOKEN": private_token,
        "Content-Type": "application/json",
    }

    created_pipelines = create_pipelines(url=url, project_ids=project_ids, reference=reference, headers=headers)
    logger.debug(created_pipelines)
    for pipeline in created_pipelines:
        print(json.dumps(pipeline))


if __name__ == "__main__":
    sys.exit(main())
