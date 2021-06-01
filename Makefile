setup:
	mkdir -p ./.venv && python3 -m venv ./.venv

env:
	#Show information about environment
	which python3
	python3 --version
	which pytest
	which pylint
install:
	pip install --upgrade pip &&\
		pip install git+git://github.com/titipata/pubmed_parser.git
lint:
	pylint --load-plugins pylint_flask --disable=R,C flask_app/*.py

test:
	pytest -vv --cov-report term-missing --cov=flask_app.web tests/test_*.py

start-api:
	#sets PYTHONPATH to directory above, would do differently in production
	cd flask_app && PYTHONPATH=".." python web.py

all: install lint test

