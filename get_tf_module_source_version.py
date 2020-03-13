"""
Goal:
  * Get the version of terraform source modules from local folders containing .tf files.

How to:
  * Get help
    - python get_tf_module_source_version..py -h
  * The path can be given as environemnt variable "TERRAFORM_PATHS
    - python get_tf_module_source_version..py --paths <path_to_terraform_file_or_folder> <another_path> <a_.tf_file>
  * The path can be given as argument (-p, --paths)
  * If the path is set both ways, "TERRAFORM_PATHS has precedence.
"""

import os
import sys
import argparse
from collections import defaultdict
import json
from threading import Thread
from queue import Queue

PATHS = os.environ.get("TERRAFORM_PATHS", [])

ALLOWED_FILE_EXTENSIONS = [".tf"]

modules_tags_queue = Queue()


def get_tags(path=""):
    filenames = []
    if os.path.isdir(path):
        for root, subFolders, files in os.walk(path):
            for name in files:
                if (
                    os.path.splitext(name)[1] in ALLOWED_FILE_EXTENSIONS
                    and root.find("/.terraform") == -1
                    and root.find("/.git") == -1
                ):
                    filenames.append(os.path.join(root, name))
    elif os.path.isfile(path):
        name = os.path.basename(path)
        if not os.path.splitext(name)[1] in ALLOWED_FILE_EXTENSIONS:
            print(f"File is not allowed {path}.")
            return
        filenames.append(path)

    module_tags = defaultdict(list)

    for name in set(filenames):
        with open(name, "r") as file_handler:
            for line in file_handler:
                line = line.strip()
                if not line and line.startswith("#"):
                    continue
                if line.find("source") >= 0 and line.find(".zip") > 0:
                    module_tags[name].append(line.split()[2].strip('"'))

    modules_tags_queue.put(module_tags)


def get_tf_module_version(paths=PATHS):
    threads = []

    for path in paths:
        if not os.path.exists(path):
            print(f"Directory/File does not exist '{path}'.")
            continue

        thread = Thread(target=get_tags, kwargs={"path": path})
        thread.daemon = True
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()  # wait for end of threads

    modules_tags = defaultdict(list)

    while not modules_tags_queue.empty():
        # module = modules_tags_queue.get()
        # modules_tags[next(iter(module))] = module[next(iter(module))]
        module_tags = modules_tags_queue.get()
        if not modules_tags:
            modules_tags = module_tags
        else:
            modules_tags.update(module_tags)
        modules_tags_queue.task_done()

    return sorted(modules_tags.items())


def main():
    parser = argparse.ArgumentParser(
        description="Get terraform source module versions.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-p", "--paths", required=True, nargs="+", help="Directories/files to check."
    )
    args = parser.parse_args()

    paths = args.paths

    modules = get_tf_module_version(paths=paths)
    print(json.dumps(modules, indent=2))


if __name__ == "__main__":
    sys.exit(main())
