
install-poetry:
	curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | POETRY_PREVIEW=1 python
	if python3 -V | grep -q '3.8'; then
		cp -r $HOME/.poetry/lib/poetry/_vendor/py3.7 $HOME/.poetry/lib/poetry/_vendor/py3.8
	fi

	pip3 install python-dotenv

install-requirements:
	poetry install

start:
	poetry run dotenv run python3 main.py --days=$(DAYS)
