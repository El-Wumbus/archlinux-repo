ARCH="x86_64"
REPONAME="archlinux-repo"
tmpdir="/tmp/${REPONAME}-old"
all: update

update: update.sh
	mkdir -p ${tmpdir}
	# cp ${ARCH}/* ${tmpdir}/
	./update.sh || rm -rf ${ARCH}/* && cp ${tmpdir}/* ${ARCH}/ && rm -rf ${tmpdir} && echo "An error occured, no packages were updated"

deploy:
	git add . && git commit -m 'updated packages [$(shell date +%s)]' && git push

clean:
	rm ./"${ARCH}"/*.db ./"${ARCH}"/*.files ./"${ARCH}"/*.tar.zst # Remove all packages