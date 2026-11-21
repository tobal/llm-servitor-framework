.PHONY: bootstrap
bootstrap:
	pipenv install -d
	./bootstrap/bootstrap-lsf.py

.PHONY: check
start:
	pipenv shell
