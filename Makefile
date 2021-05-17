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
		pip install git+git://github.com/titipata/pubmed_parser.git &&\
		python -m spacy download en_core_web_sm &&\
		pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_sm-0.4.0.tar.gz

lint:
	pylint --load-plugins pylint_flask --disable=R,C flask_app/*.py

test:
	pytest -vv --cov-report term-missing --cov=flask_app.web tests/test_*.py

start-api:
	#sets PYTHONPATH to directory above, would do differently in production
	cd flask_app && PYTHONPATH=".." python web.py

all: install lint test

