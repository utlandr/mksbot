.PHONY: test dev-venv env mypy black pytest flake8 clean

SRC := mksbot
VENV := .venv

dev-venv: $(PIPENV_FILES)
	pipenv install --dev

test: clean black mypy flake8 pytest

pytest:
	-pipenv run pytest mksbot

mypy:
	-pipenv run mypy $(SRC)

flake8:
	-pipenv run flake8 --statistics $(SRC)

black:
	-pipenv run black --check $(SRC)

clean:
	pipenv clean

