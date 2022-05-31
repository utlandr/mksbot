.PHONY: test dev-venv env mypy black pytest flake8 clean isort

SRC := mksbot
VENV := .venv

dev-venv: $(PIPENV_FILES)
	pipenv install --dev

test: black mypy flake8 pytest

pytest:
	-pytest $(SRC)

mypy:
	-mypy $(SRC)

flake8:
	-flake8 --statistics $(SRC)

black:
	-black --check $(SRC)

isort:
	-isort --check $(SRC)

clean:
	pipenv clean

