# SPDX-License-Identifier: MIT
# Gerado por scripts/prepare-make.py; dados em docs/make-labs.json.
.DEFAULT_GOAL := help
PYTHON ?= python3
export VARIANT ?= reference
export MODE ?= gpu
export EXPERIMENT ?= default
export CC
.PHONY: help setup build test run clean verify-preparation
help setup build test run clean verify-preparation:
	@$(PYTHON) materials/lab.py $@
# libFuzzer exige Clang; CC na linha de comando permite seleção explícita.
ifeq ($(origin CC),default)
CC := clang
endif
