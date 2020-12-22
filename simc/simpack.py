# simpack (stands for simC Packages) is the official package manager for simC

# Import libraries
import requests
import argparse
import os

# Import error from global helpers
from .global_helpers import error


def get_package():
    # Get path to local simc installation
    simc_path = os.path.dirname(__file__)

    # Get path for package-index which has link to download simc modules
    index_path = os.path.join(simc_path, "package-index")

    # Open the path and read all the package names with corresponding links
    with open(index_path, "r") as file:
        index = file.read().split("\n")
        package_index = {}
        for i in range(len(index)):
            name_link = index[i].split("-")
            package_index[name_link[0].strip()] = name_link[1].strip()

    # Command line argument parser
    parser = argparse.ArgumentParser(description="simC Packages")
    parser.add_argument("--name", help="Enter name of package")

    args = parser.parse_args()

    # Find the link for the package name
    requested_name = args.name
    requested_link = package_index.get(requested_name, "Unknown")

    # If the package is not listed in package-index then throw an error
    if requested_link == "Unknown":
        error("Unable to find package with name " + requested_name, -1)

    # All modules go inside modules directory in local simc installation
    module_dir = os.path.join(simc_path, "modules")
    module_path = os.path.join(module_dir, requested_name + ".simc")

    # If module directory does not exist (user did not install anything yet) then create the directory
    if not os.path.exists(module_dir):
        os.mkdir(module_dir)

    # If the simc file is already present in modules directory then the package is already installed
    if os.path.exists(module_path):
        print(requested_name + " is already installed!")
    
    # Otherwise fetch the simc module from the corresponding link
    else:
        print("Fetching package " + requested_name + " from " + requested_link)
        r = requests.get(requested_link)

        # Dump module code into modules/<module-name>.simc
        open(module_path, "wb").write(r.content)
        print(requested_name + " is now available for use!")
