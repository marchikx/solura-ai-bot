.PHONY: verify install test

verify: install test

install:
	python -m pip install -q -r requirements.txt pytest

test:
	python -m pytest -q
