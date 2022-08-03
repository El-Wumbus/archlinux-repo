#!/usr/bin/env python3
"""
Build a package from PKGBUILDs and add it to the repo
"""
import sys
import os
import argparse
import glob
import shutil
# import subprocess


def err(message: str, file=sys.stderr) -> None:
    """ Prints an error message and exit"""
    print(f"Error: {message}", file=file)
    sys.exit(1)


def rmtree(path: str) -> None:
    """Remove a file and all its contents"""
    # Ensure the absolute path is used
    if not os.path.exists(path):
        err(f"{path} does not exist")
    path = os.path.abspath(path)
    if os.path.isdir(path):
        if shutil.rmtree(path):
            err(f"Could not remove {path}")
    elif os.path.isfile(path):
        if os.remove(path):
            err(f"Could not remove {path}")
    print(f"Removing {path}")


def main() -> int:
    """main function

    Returns:
        int: exit code
    """
    # Get the current directory
    here: str = os.path.abspath(os.path.dirname(__file__))

    module_description = "Build a package from PKGBUILDs and add it to the repo"
    parser = argparse.ArgumentParser(description=module_description)
    parser.add_argument(
        "package", help="package to build and add to repo", nargs="*")
    parser.add_argument(
        "-a", "--arch", help="arch to add package to", default="x86_64", nargs="?")
    parser.add_argument(
        "-l", "--list", help="list all packages", action="store_true")
    parser.add_argument("-r", "--repo", help="repo to add package to",
                        default="archlinux-repo", nargs="?")

    # Parse the arguments
    args = parser.parse_args()
    arch = args.arch

    avalible_packages = os.listdir(os.path.join(here, "pkgbuilds"))

    # Printing all the avalible packages and exiting.
    if args.list:
        print("\n".join(avalible_packages))
        return 0

    # If no package is specified, it will print an error message and exit.
    if not args.package:
        err("No package specified")
    if "all" in args.package:
        args.package = avalible_packages
        print("Building all packages")
    # Removing all the `*.db`, and `*.files` files in the `arch` directory.
    for item in glob.glob(os.path.join(here, arch, "*.db")):
        rmtree(item)
    for item in glob.glob(os.path.join(here, arch, "*.files")):
        rmtree(item)

    for package in args.package:
        print("Building package:", package)
        if package in avalible_packages:

            # Removing all the packages that match the pattern `{package}*.pkg.tar.xz`
            for item in glob.glob(os.path.join(here, arch, f"{package}*.pkg.tar.zst")):
                rmtree(item)

            os.chdir(os.path.join(here, "pkgbuilds", package))

            # Build the package
            if os.system("makepkg -scf"):
                return 1

            # Move the package to the repo
            for pkg_tarball in glob.glob("*.pkg.tar.zst"):
                shutil.move(pkg_tarball, os.path.join(here, arch))

            for item in os.listdir(os.path.abspath(".")):
                if not "PKGBUILD" in item:
                    # Ensure the absolute path is used
                    item = os.path.abspath(item)

                    rmtree(item)
                    print(f"Removing {item}")
            os.chdir(here)

    # Rebuilding the repo
    os.chdir(os.path.join(here, arch))
    os.system(f"repo-add {args.repo}.db.tar.gz ./*.tar.zst")
    for file in glob.glob("*.tar.gz"):
        file2 = ".".join(file.split(".")[:-2])
        shutil.move(os.path.abspath(file), os.path.abspath(file2))
    os.chdir(here)
    return 0

if __name__ == "__main__":
    sys.exit(main())
