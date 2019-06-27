# gitlab  helpers

## Get unestimated issues in gitlab

`get_unestimated_issues.py`

Goal:
  * Get unestimated issue over all gitlab projects assigned to a specific user

How to:
  * Get help
    - `python get_unestimated_issues.py -h`
  * The **Private Token** can be given as environemnt variable `GITLAB_PRIVATE_TOKEN`
    - I read the password using pass (cli password manager)
    - `GITLAB_PRIVATE_TOKEN=$(pass show work/CSS/gitlab/private_token) python get_unestimated_issues.py --user <user_name> --url <gitlab_url>`
  * The **Private Token** can be given as argument (`-t`, `--token`)
    - `python get_unestimated_issues.py --token $(pass show work/CSS/gitlab/private_token) --user <user_name> --url <gitlab_url>`
  * If the **Private Token** is set both ways, `GITLAB_PRIVATE_TOKEN` has precedence.
  * The **user** can be given as argument (`-l`, `--user`)

Optimizations:
  * Implement pagination and make sure to get ALL the projects and issues.


## Get most recent tags from repositories

`get_most_recent_tag.py`

The tool takes a group id and lists all the tags of the contained repositories.

Goal:
  * Get most recent tags of the repositories within a group.

How to:
  * Get help
    - `python get_most_recent_tag.py -h`
  * The **Private Token** can be given as environemnt variable `GITLAB_PRIVATE_TOKEN`
    - I read the password using pass (cli password manager)
    - `GITLAB_PRIVATE_TOKEN=$(pass show work/CSS/gitlab/private_token) python get_most_recent_tag.py --url <gitlab_url> --group <gitlab_group_id>`
  * The **Private Token** can be given as argument (`-t`, `--token`)
    - `python get_most_recent_tag.py --token $(pass show work/CSS/gitlab/private_token) --url <gitlab_url> -- group <gitlab_group_id>`
  * If the **Private Token** is set both ways, `GITLAB_PRIVATE_TOKEN` has precedence.
  * The **gitlab group id** can be given as environemnt variable `GITLAB_GROUP_ID`
  * The **gitlab group id** can be given as argument (`-g`, `--group`)
  * If the **gitlab group id** is set both ways, `GITLAB_GROUP_ID` has precedence.
  * The **url** can be given as argument (`-u`, `--user`)
  * The output can be limited to only the most recent tags of each repository (`-l`, `--latest`)

## Get source module version used in local directories

`get_tf_module_source_version.py`

I use zipped terraform modules, which are stored in an AWS S3 bucket, like this:
```
source = s3::https://s3-eu-west-1.amazonaws.com/tf-modules/tf-module/tf-module-1.2.2.zip
```

This tool is called with a directory or a file or several of them (also mixed directoriess and files).
It expects directories containing terraform configurations or `main.tf` files.

Up to now, only `main.tf` files are checked.

The script eventually returns files and source modules found within, like this:
```
/path_to_repo.git/tf_service/main.tf
  "s3::https://s3-eu-west-1.amazonaws.com/tf-modules/tf-module-service/tf-module-service-1.2.5.zip"
/path_to_repo.git/tf_module/main.tf
  "s3::https://s3-eu-west-1.amazonaws.com/tf-modules/tf-module/tf-module-1.2.2.zip"
/path_to_repo.git/tf_service1/main.tf
  "s3::https://s3-eu-west-1.amazonaws.com/tf-modules/tf-module-service/tf-module-service-1.2.5.zip"
/path_to_repo.git/tf_network/main.tf
  "s3::https://s3-eu-west-1.amazonaws.com/tf-modules/tf-module-network/tf-module-network-1.1.zip"
```
