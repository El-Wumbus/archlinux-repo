import os
import sys
from glob import glob
from rich.console import Console
from rich import print as printr
from rich.prompt import Confirm
import subprocess
import shutil

REPONAME = "archlinux-repo"
ARCH = "x86_64"
STARTINGDIR = os.path.abspath(".")
# Creating a console object that can be used to print to the terminal.
console = Console()
TEMPDIR = "/tmp"
# Joining the current directory with the arch variable.
REPODIR = os.path.join(".", ARCH)


def ERR(message: str, code: int):
    """
    Prints a message and exits the program with a given exit code

    :param message: The message to print to the console
    :type message: str
    :param code: The exit code to exit with
    :type code: int
    """
    if message != None:
        console.log(f"[bold red]{message}")
    else:
        console.log("[bold red]An unknown error has occured")

    if code != None:
        sys.exit(code)
    else:
        sys.exit(1)


def backuppackage(pkg: str, TEMPDIR: str):
    """
    Creates a backup directory in /tmp and copies the packages to it.

    :param pkg: The package name
    :type pkg: str
    :param TEMPDIR: The directory where the script will be run
    :type TEMPDIR: str
    """
    # Creating a backup directory in /tmp and copying the packages to it.
    backupdir = os.path.join(TEMPDIR, "old-packages")
    if not os.path.exists(backupdir):
        os.mkdir(backupdir)  # make backup directory
    for package in glob(f"{pkg}*.tar.zst"):
        shutil.copy(os.path.abspath(package), backupdir)
        os.remove(os.path.abspath(package))


def cleanrepo(REPODIR):
    """
    Removes all the files in the repo directory

    :param REPODIR: The directory where the repo is located
    """
    # Removing all the files in the repo directory.
    for oldgarbage in glob("*", root_dir=REPODIR):
        try:
            os.remove(oldgarbage)
        except:
            ERR(f"Failed to remove {oldgarbage}", 1)


def restorepackages(REPODIR):
    """
    It copies the packages from the backup directory to the repo directory

    :param REPODIR: The directory of the repo
    """
    # Copying the packages from the backup directory to the repo directory.
    backupdir = os.path.join(TEMPDIR, "old-packages")
    for package in glob("*", root_dir=backupdir):
        try:
            shutil.copy(package, REPODIR)
        except:
            ERR(f"Failed to restore {package}", 1)
    os.chdir(STARTINGDIR)


def makepackage(dir: str):
    """
    Removes all the packages from the repo directory, and then builds a new package assuming the name of
    the directory that was passed to the function is the package name

    :param dir: package name
    :type dir: str
    """
    for package in glob("*", root_dir=REPODIR):
        try:
            # removing the package from the repo directory.
            os.remove(os.path.join(os.path.abspath(REPODIR), package))
        except:
            ERR(f"Failed to remove {package}", 1)
    dirorg = dir
    # It's changing the directory to the pkgbuild directory and then changing back to the starting
    # directory.
    dir = os.path.join("pkgbuilds", dir)
    os.chdir(STARTINGDIR)
    fulldirpath = os.path.abspath(dir)
    print(fulldirpath)
    os.chdir(fulldirpath)

    for file in glob("*.tar.zst"):

        if os.path.exists(file):
            shutil.copy(file, REPODIR)

            # Removing the package file after it's been copied to the repo.
            os.remove(file)
    exitcode = subprocess.check_output(
        "makepkg >> /dev/null || exit $?", shell=True, stderr=subprocess.DEVNULL)

    # Exit with error if makepkg fails
    if exitcode:
        restorepackages(REPODIR)
        ERR("Makepkg Error", exitcode)

    # Remove leftover package trash
    for trash in glob("*.deb") or glob("*.tar") or glob("*.md"):
        os.remove(trash)

    # Removing the pkg and src directories that are created by makepkg.
    shutil.rmtree(os.path.abspath("./pkg"))
    shutil.rmtree(os.path.abspath("./src"))
    path1 = os.path.join("./", dirorg)
    if os.path.exists(path1):
        shutil.rmtree(path1)

    # Copying the package to the repo directory.
    for file in glob("*.tar.zst"):
        shutil.copy(file, REPODIR)
    os.chdir(STARTINGDIR)
    return(0)


# Getting the list of directories in the pkgbuilds directory.
dirpkgbuild = "pkgbuilds"
pkgbuild_dirlist = os.listdir(dirpkgbuild)

# Creating tasks that will be used to show the progress of the build.
tasks = [f"package {n}" for n in range(1, (len(pkgbuild_dirlist) + 1))]

# Print the packages to build
console.print("[bold green][u]Package list:[/u]\n")
for package in pkgbuild_dirlist:
    console.print(f"[#7289DA]{package}")

# Ask to continue
if not Confirm.ask("Continue?"):
    sys.exit(0)

# Make packages
# Shows the progress of the build.
with console.status("[bold green]Building Packages...") as status:
    while tasks:
        # Looping through the list of directories in the pkgbuilds directory and then calling the
        # backuppackage function, makepackage function, and then printing the name of the package
        # that was built.
        for dir in pkgbuild_dirlist:
            task = tasks.pop(0)
            backuppackage(dir, TEMPDIR)
            makepackage(dir)
            console.log(f"[bold blue]{dir} done")

# Making the repo files.
os.chdir(REPODIR)  # Changing the directory to the repo directory.

repobuildtasks = [f"repo {n}" for n in range(1, 1)]
with console.status("[bold green]Building Repo...") as status:
    while repobuildtasks:
        repobuildtask = repobuildtasks.pop(0)
        # Removing all the files in the repo directory, and then making the repo files.
        cleanrepo(REPODIR, TEMPDIR)
        exitcode = subprocess.call(
            "repo-add archlinux-repo.db.tar.gz ./*.tar.zst")

        # Removing the symlinks and replacing them with the actual files.
        os.unlink("archlinux-repo.db")
        os.unlink("archlinux-repo.files")
        shutil.move(os.path.abspath("archlinux-repo.db.tar.gz"),
                    os.path.join(os.path.abspath("."), "archlinux-repo.db"))
        shutil.move(os.path.abspath("archlinux-repo.files.tar.gz"),
                    os.path.join(os.path.abspath("."), "archlinux-repo.files"))

        console.log(f"[bold blue]archlinux-repo done")
os.chdir(STARTINGDIR)
exit()
