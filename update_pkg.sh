#!/usr/bin/env bash

rm ./x86_64/*.db ./x86_64/*.files ./x86_64/*.tar.zst # Remove all packages

### Build every packakge and copy it to the x86_64 repo ###
for dir in pkgbuilds/*/     # list directories in the form "/tmp/dirname/"
do     dir=${dir%*/}      # remove the trailing "/"
    cd "${dir}" || exit
    makepkg
    cp ./*.tar.zst ../../x86_64/
    rm -rf pkg src ./*.tar.zst "${dir##*/}"
    cd ../..
done

cd ./x86_64 || exit
repo-add archlinux-repo.db.tar.gz ./*.tar.zst
rm archlinux-repo.db
rm archlinux-repo.files
cp archlinux-repo.files.tar.gz archlinux-repo.files
cp archlinux-repo.db.tar.gz archlinux-repo.db
rm archlinux-repo.db.tar.gz
rm archlinux-repo.files.tar.gz
