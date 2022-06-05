import os
import sys
from glob import glob
from rich.console import Console
import subprocess
import shutil

REPONAME = "archlinux-repo"
ARCH = "x86_64"
STARTINGDIR = os.path.abspath(".")
console = Console()
TEMPDIR = "/tmp"
REPODIR = os.path.join(".", ARCH)

def ERR(message:str, code:int):
  """Print error message in red and exit with an error code

  Args:
      message (str): The message to print
      code (int): The exit code
  """
  if message != None: console.log(f"[bold red]{message}")
  else: console.log("[bold red]An unknown error has occured")

  if code != None: sys.exit(code)
  else: sys.exit(1)

def uconfirm(message:str):
  """Ask the user for conformation on a message (Favors the 'N' answer)

  Args:
      message (str): The message to print
  """
  
  print(f"{message} [y/N]: ", end = '')
  answer = input()

  if answer != 'y' or 'Y': return(False)
  else: return(True)
  
def backuppackage(pkgdir:str, TEMPDIR:str):
  backupdir = os.path.join(TEMPDIR, "old-packages")
  os.mkdir(backupdir) # make backup directory
  shutil.copy(pkgdir, "backupdir")

def cleanrepo(REPODIR):
  
  for oldgarbage in glob("*", root_dir=REPODIR):
    try: os.remove(oldgarbage)
    except: ERR(f"Failed to remove {oldgarbage}", 1)

def restorepackages(REPODIR):
  backupdir = os.path.join(TEMPDIR, "old-packages")
  for package in glob("*", root_dir=backupdir):
    try: shutil.copy(package, REPODIR)
    except: ERR(f"Failed to restore {package}", 1)
  
  os.chdir(STARTINGDIR)

def makepackage(dir:str):
  
  for package in glob("*", root_dir=REPODIR):
    try: os.remove(package)
    except: ERR(f"Failed to remove {package}", 1)
  dirorg = dir
  dir = os.path.join("pkgbuilds", dir)   
  fulldirpath = os.path.abspath(dir)
  os.chdir(fulldirpath)
  
  exitcode = subprocess.call("makepkg >> /dev/null || exit $?", shell = True)
  # Exit with error if makepkg fails
  if exitcode:
    restorepackages(REPODIR)
    ERR("Makepkg Error", exitcode)
  
  # Remove leftover makepkg trash
  for trash in glob("*.deb") or glob("*.tar") or glob("*.md"):
    os.remove(trash)
    
  shutil.rmtree(os.path.abspath("./pkg"))
  shutil.rmtree(os.path.abspath("./src"))
  shutil.rmtree(os.path.abspath(os.path.join("./", dirorg)))
  shutil.copy(glob("*.tar.zst"))
  os.chdir(STARTINGDIR)
  
dirpkgbuild = "pkgbuilds"
pkgbuild_dirlist = os.listdir(dirpkgbuild)

tasks = [f"package {n}" for n in range(1, (len(pkgbuild_dirlist) + 1))]
with console.status("[bold green]Building Packages...") as status:
  while tasks:
    for dir in pkgbuild_dirlist:
      task = tasks.pop(0)
      backuppackage(dir, TEMPDIR)
      makepackage(dir)
      console.log(f"[bold blue]{dir} done")

os.chdir(REPODIR)
repobuildtasks = [f"repo {n}" for n in range(1,1)]
with console.status("[bold green]Building Repo...") as status:
  while repobuildtasks:
    repobuildtask = repobuildtasks.pop(0)
    cleanrepo(REPODIR, TEMPDIR)
    exitcode = subprocess.call("repo-add archlinux-repo.db.tar.gz ./*.tar.zst")
    
    # Fix repo files
    os.unlink("archlinux-repo.db")
    os.unlink("archlinux-repo.files")
    shutil.move(os.path.abspath("archlinux-repo.db.tar.gz"), os.path.join(os.path.abspath("."), "archlinux-repo.db"))
    shutil.move(os.path.abspath("archlinux-repo.files.tar.gz"), os.path.join(os.path.abspath("."), "archlinux-repo.files"))
    
    console.log(f"[bold blue]archlinux-repo done")
os.chdir(STARTINGDIR)
exit