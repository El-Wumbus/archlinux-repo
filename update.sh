#!/usr/bin/env bash
REPONAME="archlinux-repo"

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

rm ./"${ARCH}"/*.db ./"${ARCH}"/*.files ./"${ARCH}"/*.tar* ./"${ARCH}"/*.deb ./"${ARCH}"/*.md
### Build every packakge and copy it to the repo ###
for dir in pkgbuilds/*/     # list directories in the form "/tmp/dirname/"
do     dir=${dir%*/}      # remove the trailing "/"
    cd "${dir}" || exit $?
    makepkg
    cp ./*.tar.zst ../../"${ARCH}"/
    sudo rm -rf pkg src ./*.tar* "${dir##*/}" || exit $?
    cd ../.. || exit $?
done

cd ./"${ARCH}" || exit $?
repo-add ${REPONAME}.db.tar.gz ./*.tar.zst
rm ${REPONAME}.db
rm ${REPONAME}.files
cp ${REPONAME}.files.tar.gz ${REPONAME}.files 
cp ${REPONAME}.db.tar.gz ${REPONAME}.db 
rm ${REPONAME}.db.tar.gz 
rm ${REPONAME}.files.tar.gz 
exit 0