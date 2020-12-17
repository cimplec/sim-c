# simpack (stands for simC Packages) is the official package manager for simC
import requests
import argparse
import os

from .global_helpers import error


def get_package():
    simc_path = os.path.dirname(__file__)
    index_path = os.path.join(simc_path, "package-index")

    with open(index_path, "r") as file:
        index = file.read().split("\n")
        package_index = {}
        for i in range(len(index)):
            name_link = index[i].split("-")
            package_index[name_link[0].strip()] = name_link[1].strip()

    parser = argparse.ArgumentParser(description="simC Packages")
    parser.add_argument("--name", help="Enter name of package")

    args = parser.parse_args()

    requested_name = args.name
    requested_link = package_index.get(requested_name, "Unknown")

    if requested_link == "Unknown":
        error("Unable to find package with name " + requested_name, -1)

    module_dir = os.path.join(simc_path, "modules")
    module_path = os.path.join(module_dir, requested_name + ".simc")

    if not os.path.exists(module_dir):
        os.mkdir(module_dir)

    if os.path.exists(module_path):
        print(requested_name + " is already installed!")
    else:
        print("Fetching package " + requested_name + " from " + requested_link)
        r = requests.get(requested_link)

        open(module_path, "wb").write(r.content)
        print(requested_name + " is now available for use!")
