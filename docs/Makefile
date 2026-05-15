# Minimal makefile for Jupyter Book documentation

BOOKDIR = .

.PHONY: help html clean

help:
	@echo "Targets:"
	@echo "  make html   Build Jupyter Book HTML docs"
	@echo "  make clean  Remove build artifacts"

html:
	jupyter-book build $(BOOKDIR)

clean:
	rm -rf _build
