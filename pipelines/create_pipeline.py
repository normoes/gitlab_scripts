"""
Goal:
  * Create Pipeline.

How to:
  * Get help
    - python create_pipeline.py -h
  * The Private Token can be given as environemnt variable GITLAB_PRIVATE_TOKEN
    - I read the password using pass (cli password manager)
    - GITLAB_PRIVATE_TOKEN=$(pass show work/CSS/gitlab/private_token) python create_pipeline.py --url <gitlab_url> --reference <branch_tag_or_other_reference> --project <gitlab_project_id>
  * The Private Token can be given as argument (-t, --token)
    - python create_pipeline.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url> --reference <branch_tag_or_other_reference> --project <gitlab_project_id>
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
PROJECT_ENDPOINT = "/projects" + "/{project_id}"
REFERENCE_PARAMETER = "?ref={reference}"
PIPELINE_ENDPOINT = "/pipeline" + f"{REFERENCE_PARAMETER}"
PROJECT_TAGS_ENDPOINT = f"{PROJECT_ENDPOINT}" + f"{PIPELINE_ENDPOINT}"


def create_pipeline(
    url=environment_variables.URL,
    project_id=environment_variables.PROJECT_ID,
    reference=environment_variables.REFERENCE,
    headers=None,
):
    url = url + GITHUB_API_ENDPOINT

    project_endpoint = PROJECT_ENDPOINT.format(project_id=quote_plus(str(project_id)))
    complete_url = (
        url + project_endpoint + PIPELINE_ENDPOINT.format(reference=reference)
    )
    response = requests.post(url=complete_url, headers=headers)
    if response.status_code not in [200, 201]:
        error = {
            "message": "Cannot create pipeline.",
            "reason": f"Received status code {response.status_code} with {response.text}.",
            "project_id": project_id,
        }
        logger.error(error)
        return {
            "error": error,
            "project_id": project_id,
            "url": complete_url,
        }

    json_response = response.json()
    logger.debug(json_response)

    pipeline_id = json_response.get("id", None)
    ref = json_response.get("ref", None)
    yaml_errors = json_response.get("yaml_errors", None)
    status = json_response.get("status", None)
    web_url = json_response.get("web_url", None)

    return {
        "pipeline_id": pipeline_id,
        "project_id": project_id,
        "reference": reference,
        "ref": ref,
        "status": status,
        "yaml_errors": yaml_errors,
        "web_url": web_url,
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
    reference = args.reference
    url = args.url

    headers = {
        "PRIVATE-TOKEN": private_token,
        "Content-Type": "application/json",
    }

    created_pipeline = create_pipeline(
        url=url, project_id=project_id, reference=reference, headers=headers
    )
    print(created_pipeline)


if __name__ == "__main__":
    sys.exit(main())
