#!/usr/bin/env bash
if [ $# -gt 0 ];then 
    while [[ $# -gt 0 ]]; do
      case $1 in
        x86|32)
        ARCH="x86";;

        x86_64|64)
          ARCH="x86_64";;
      esac
    done
else
    ARCH="x86_64"
fi

rm ./"${ARCH}"/*.db ./"${ARCH}"/*.files ./"${ARCH}"/*.tar.zst || exit 1 # Remove all packages

### Build every packakge and copy it to the repo ###
for dir in pkgbuilds/*/     # list directories in the form "/tmp/dirname/"
do     dir=${dir%*/}      # remove the trailing "/"
    cd "${dir}" || exit $?
    makepkg || exit $?
    cp ./*.tar.zst ../../"${ARCH}"/ || exit $?
    rm -rf pkg src ./*.tar* "${dir##*/}" || exit $?
    cd ../.. || exit $?
done

cd ./"${ARCH}" || exit $?
repo-add archlinux-repo.db.tar.gz ./*.tar.zst
rm archlinux-repo.db
rm archlinux-repo.files
cp archlinux-repo.files.tar.gz archlinux-repo.files 
cp archlinux-repo.db.tar.gz archlinux-repo.db 
rm archlinux-repo.db.tar.gz 
rm archlinux-repo.files.tar.gz 
exit 0