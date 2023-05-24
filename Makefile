SRC := src
PACKAGE := mksbot

.PHONY: help
help:
	@echo "Available targets:"
	@egrep "^([a-zA-Z_-]+):.*" $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":"}; {printf "    \033[36m%s\n\033[0m", $$1}'
	@echo ""
	@echo "Hints:"
	@echo "    Use '-n' to do a dry run"
	@echo "    Use '-k' to ignore failed targets and keep going"


.PHONY: create-egg-base
create-egg-base:
	@echo
	mkdir -p build/egg_base

.PHONY: init
init: create-egg-base
	@echo
	pip install -e .

.PHONY: clean
clean:
	@echo
	rm -rf build/
	find ${SRC} | grep -E "(\.egg-info|__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf
