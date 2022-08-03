# Archlinux-repo

## Installation

Add the following to the end of your `/etc/pacman.conf` file

```ini
[archlinux-repo]
SigLevel = Optional TrustAll
Server = https://raw.githubusercontent.com/El-Wumbus/$repo/master/$arch
```

Force Sync with the repo

```bash
sudo pacman -Syy
```

## Usage

Use like any other repo.

Example:

```txt
$ sudo pacman -S quickalias --noconfirm
resolving dependencies...
looking for conflicting packages...

Packages (1) quickalias-r54.r6380bee.-1

Total Installed Size:  0.01 MiB
Net Upgrade Size:      0.00 MiB

:: Proceed with installation? [Y/n]
:: Retrieving packages...
...
```
