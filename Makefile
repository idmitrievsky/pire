.PHONY: install docs test

install:
	pip install .

docs:
	pycco pire/core.py
	mv docs/core.html docs/index.html

test:
	pip install -r requirements.txt
	pytest
