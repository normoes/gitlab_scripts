#!/usr/bin/env python
from git import Repo
import argparse
import os
import re
import sys

"""
Goal:
  * Check included .gitlab-ci.yml references.

How to:
  * Get help
    - check_included_ci_ref.py -h
    - python check_included_ci_ref.py --file <path_to_gitlab_ci_file>
  * The file can be given as argument (-f, --file)
"""

parser = argparse.ArgumentParser(description='Check ref of included .gitlab-ci.yml files.', epilog="python check_included_ci_ref.py --file <path_to_gitlab_ci_file>", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-f', '--file', default="./.gitlab-ci.yml", help='Path to .gitlab-ci yml file.')
args = parser.parse_args()

GITLAB_CI_FILE = args.file

REF_LINE = re.compile("^[ ]*ref:[ ] *(\w*)")

STAGING_BRANCH = "staging"
MASTER_BRANCH = "master"

BRANCH_REF_MAP = {
    STAGING_BRANCH: (STAGING_BRANCH, MASTER_BRANCH),
    MASTER_BRANCH: (MASTER_BRANCH),
}


def get_appropriate_ref(ref_line, branch):
    print(f"Branch: {branch}")
    print(f"Line: {ref_line}")
    # reference = REF_LINE.findall(ref_line, re.IGNORECASE)[0]
    reference = REF_LINE.findall(ref_line)[0]

    if not reference in BRANCH_REF_MAP[branch]:
        if STAGING_BRANCH == branch:
            new_reference = STAGING_BRANCH
        elif MASTER_BRANCH == branch:
            new_reference = MASTER_BRANCH
    else:
        new_reference = reference

    print(f"--- {reference}")
    print(f"--- {new_reference}")
    print(f"--- {ref_line}")
    # replaced_line = re.sub(reference, new_reference, ref_line, flags=re.IGNORECASE)
    replaced_line = re.sub(reference, new_reference, ref_line)
    print(f"--- {replaced_line}")
    return replaced_line


def check_included_refs(file_path=GITLAB_CI_FILE):
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        print("Is this the correct file?")
        sys.exit(1)
    abs_path = os.path.abspath(GITLAB_CI_FILE)
    base_path = os.path.dirname(GITLAB_CI_FILE)
    file_name = os.path.basename(GITLAB_CI_FILE)
    print(abs_path)
    print(base_path)
    print(file_name)
    # Get current branch
    repo = Repo(base_path)
    branch = repo.active_branch.name
    print(branch)
    # Replace refs used in .gitlba-ci.yml
    content = None
    with open(file_path, "r") as file_handler:
        content = file_handler.readlines()
    if not branch in BRANCH_REF_MAP:
        print(f"No ref preference on branch \"{branch}\".")
        return content
    new_content = list()
    if not content:
        print("File is empty.")
        sys.exit(1)
    replaced = False
    for line in content:
        # line = line.strip()
        # if line:
        # if REF_LINE.match(line, re.IGNORECASE):
        if REF_LINE.match(line):
            new_line = get_appropriate_ref(ref_line=line, branch=branch)
            if new_line != line:
                replaced = True
        else:
            new_line = line
        new_content.append(new_line)
    if replaced:
        with open(file_path, "w") as file_handler:
            file_handler.write("".join(new_content))
        print(f"Refs replaced in {file_path}")


if __name__ == "__main__":
    check_included_refs()
