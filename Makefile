$(eval INTERNALREQ=$(shell python -c "import configparser; cfg=configparser.ConfigParser(); cfg.read('setup.cfg'); u = ' '.join([f'--upgrade-package {p}' for p in cfg['options']['install_requires'].split('\n') if p != '']); print(u)"))

sync:
	pip-sync requirements/prod.txt requirements/dev.txt requirements/test.txt
	pip install -e . --no-deps
compile-prod:
	pip-compile --no-header setup.py --output-file requirements/prod.txt $(INTERNALREQ)
compile-test:
	pip-compile --no-header requirements/test.in --output-file requirements/test.txt $(INTERNALREQ)
compile-dev:
	pip-compile --no-header requirements/dev.in --output-file requirements/dev.txt $(INTERNALREQ)
full-compile:	compile-prod compile-test compile-dev
