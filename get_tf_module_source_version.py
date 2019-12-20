import os
import sys
import argparse
from collections import defaultdict
import json

"""
Goal:
  * Get the version of terraform source modules from local folders containing .tf files.

How to:
  * Get help
    - python get_tf_module_source_version..py -h
  * The path can be given as environemnt variable "TERRAFORM_PATH
    - python get_tf_module_source_version..py --path <path_to_terraform_file_or_folder>
  * The path can be given as argument (-p, --path)
  * If the path is set both ways, "TERRAFORM_PATH has precedence.
"""
PATH = os.environ.get("TERRAFORM_PATH", None)

parser = argparse.ArgumentParser(description='Get terraform source module versions.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-p', '--path', required=True, nargs="+", help='Directory/file to check.')
args = parser.parse_args()

if not PATH:
    PATH = args.path

ALLOWED_FILE_EXTENSIONS = [".tf"]


def get_tf_module_version(paths=PATH):
    modules = defaultdict(list)
    filenames = list()
    for path in paths:
        if not os.path.exists(path):
            print(f"Directory/File does not exist '{path}'.")
            continue
        if os.path.isdir(path):
            for root, subFolders, files in os.walk(path):
                for name in files:
                    if os.path.splitext(name)[1] in ALLOWED_FILE_EXTENSIONS and root.find("/.terraform") == -1 and root.find("/.git") == -1:
                        filenames.append(os.path.join(root, name))
        elif os.path.isfile(path):
            name = os.path.basename(path)
            if not os.path.splitext(name)[1] in ALLOWED_FILE_EXTENSIONS:
                print(f"File is not allowed {path}.")
                continue
            filenames.append(path)

    for name in set(filenames):
        with open(name, "r") as file_handler:
            for line in file_handler:
                line = line.strip()
                if not line and line.startswith("#"):
                    continue
                if line.find("source") >= 0 and line.find(".zip") > 0:
                    modules[name].append(line.split()[2].strip("\""))
    return modules


def main():
    modules = get_tf_module_version()
    print(json.dumps(modules, indent=2))
    # for k, v in modules.items():
    #     print(k)
    #     print("  " +  "\n  ".join(t.split()[2] for t in v))

if __name__ == '__main__':
    sys.exit(main())
