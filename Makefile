.PHONY: publish

publish:
	tox -e packaging
	twine upload -s dist/*
