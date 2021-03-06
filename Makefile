

deps:
	python3 -m pip install --user --upgrade setuptools wheel
	python3 -m pip install --user --upgrade twine

build: deps
	python3 setup.py sdist bdist_wheel


twine: build
	python3 -m twine upload dist/*
