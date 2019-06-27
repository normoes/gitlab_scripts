import os
import argparse
from collections import defaultdict

PATH = os.environ.get("TERRAFORM_PATH", None)

parser = argparse.ArgumentParser(description='Get terraform source module versions.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-p', '--path', required=True, nargs="+", help='Directory/file to check.')
args = parser.parse_args()

if not PATH:
    PATH = args.path

ALLOWED_FILES = ["main.tf"]


def get_tf_module_version(paths=PATH):
    modules = defaultdict(list)
    filenames = list()
    for path in paths:
        if not os.path.exists(path):
            print(f"Directory/File does not exist {path}.")
            continue
        if os.path.isdir(path):
            for root, subFolders, files in os.walk(path):
                for name in files:
                    if name in ALLOWED_FILES and root.find("/.terraform") == -1 and root.find("/.git") == -1:
                        filenames.append(os.path.join(root, name))
        elif os.path.isfile(path):
            name = os.path.basename(path)
            if not name in ALLOWED_FILES:
                print(f"File is not allowed {path}.")
                continue
            filenames.append(path)

    for name in set(filenames): 
        with open(name, "r") as file_handler:
            for line in file_handler:
                line = line.strip()
                if line.startswith("#"):
                    continue
                if line.find("source") >= 0 and line.find(".zip") > 0:
                    modules[name].append(line)
    return modules

if __name__ == '__main__':
    modules = get_tf_module_version()
    for k, v in modules.items():
        print(k)
        print("  " +  "\n  ".join(t.split()[2] for t in v)) 
