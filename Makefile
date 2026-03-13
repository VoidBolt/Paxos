# Makefile for Paxos project

ID ?= 0
CONFIG ?= cluster_subnet.json
REPO_URL := https://github.com/VoidBolt/Paxos.git
VENV_DIR := venv

# Clone repo (only if it doesn't exist)
clone:
	@test -d Paxos || git clone $(REPO_URL)

# Create virtual environment (only if it doesn't exist)
$(VENV_DIR)/bin/activate:
	python3 -m venv $(VENV_DIR)

# Install dependencies
install: $(VENV_DIR)/bin/activate
	. $(VENV_DIR)/bin/activate && pip install -e .

# Run the Paxos node
run: install
	. $(VENV_DIR)/bin/activate && \
	python3 src/paxos/paxos_async.py --config $(CONFIG) --node_id $(ID)

# Convenience: setup everything
setup: clone install

.PHONY: clone install run setup
