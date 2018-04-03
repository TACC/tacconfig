version := $(shell cat VERSION)

.PHONY: sdist docs clean dist-clean release tests preflight tag
.SILENT: sdist docs clean dist-clean release tests preflight tag

sdist: dist-clean
	python setup.py sdist && \
	make clean

# docs:
# 	cd docs && \
# 	make html

install:
	python setup.py install

clean:
	rm -rf config/tests/*pyc config/*pyc config.egg-info build/ .cache config/tests/__pycache__ .pytest_cache && \
	cd docs && \
	make clean

dist-clean: clean
	rm -rf dist

tests:
	tox

prerelease: sdist
	git add . && \
	git commit -m "Releasing ${version}"

preflight:
	echo "checking git repo is in shape for release"
	bash scripts/checkrepo.sh

release: preflight
	echo "git tag will be: $(version)"
	git tag -f "${version}"
	git push origin "${version}"
