ARCH="x86_64"

all: update

update: update.sh
	mkdir -p old
	cp ${ARCH}/* old/
	./update.sh || rm -rf ${ARCH}/* && cp old/* ${ARCH}/ && rm -rf old; echo "An error occured, no packages were updated"

deploy:
	git add . && git commit -m 'updated packages $(shell date +%s)' && git push

clean:
	rm ./"${ARCH}"/*.db ./"${ARCH}"/*.files ./"${ARCH}"/*.tar.zst # Remove all packages