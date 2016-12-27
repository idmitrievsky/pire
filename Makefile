install:
	pip install .

test:
	pip install -r requirements.txt
	pytest
