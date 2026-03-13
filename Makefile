# Makefile for setting up and running the Paxos project

# Default node ID (can be overridden)
ID ?= 0

# Repository and virtual environment
REPO_URL := https://github.com/VoidBolt/Paxos.git
VENV_DIR := venv
CONFIG   := cluster_subnet.json

# Target: clone the repository
clone:
	git clone $(REPO_URL)

# Target: create virtual environment
venv:
	python3 -m venv $(VENV_DIR)

# Target: install the package in editable mode
install: venv
	. $(VENV_DIR)/bin/activate && pip install -e .

# Target: run the Paxos node
run: install
	. $(VENV_DIR)/bin/activate && \
	python3 src/paxos/paxos_async.py --config $(CONFIG) --node_id $(ID)

# Convenience target: setup everything
setup: clone install

.PHONY: clone venv install run setup
