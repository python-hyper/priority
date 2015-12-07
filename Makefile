.PHONY: publish

publish:
	python setup.py sdist upload
	python setup.py bdist_wheel upload

