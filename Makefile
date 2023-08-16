dev:
	$(MAKE) setup-venv
	$(MAKE) setup-pipx
	$(MAKE) setup-cli
	$(MAKE) lock-dev
	$(MAKE) sync-dev

lock-dev:
	$(info "[*] Locking dev dependencies")
	pip-compile --generate-hashes -o dev-requirements.txt dev-requirements.in

sync-dev:
	$(info "[*] Synchronizing virtual environment with locked dev dependencies")
	pip-sync dev-requirements.txt

upgrade-dev:
	$(info "[*] Upgrading all dev dependencies")
	pip-compile --upgrade dev-requirements.in
	$(MAKE) lock-dev
	$(MAKE) sync-dev

setup-venv:
	$(info "[*] Setting up a virtual environment")
	python3 -m venv .venv
	. .venv/bin/activate

setup-cli:
	pipx install pip-tools==7.3.0 
	pipx install aws-sam-cli==1.95.0

setup-pipx:
	pip install pipx
	pipx ensurepath
