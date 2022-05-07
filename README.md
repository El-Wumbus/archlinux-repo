archlinux-repo
==============

A package repo for arch linux

Usage
-----

1. Add the folowing to your `/etc/pacman.conf` file

        [archlinux-repo]
        SigLevel = Optional TrustAll
        Server = https://raw.githubusercontent.com/El-Wumbus/$repo/Master/$arch

2. Update your repos

        sudo pacman -Syyu

3. Install a package like normal

        sudo pacman -S better-discord-installer
