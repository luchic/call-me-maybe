#!/usr/bin/env bash


VENV="$HOME/goinfre/prcache/venv"
PROJECT_ENV="$VENV/call-me-maybe"

if [[ ! -d "$VENV" ]]; then
	mkdir -p "$VENV"
fi

if [[ ! -f "$PROJECT_ENV/bin/activate" ]]; then
	python3 -m venv "$PROJECT_ENV"
fi

if [[ ! -d "$VENV/pipcache" ]]; then
	mkdir -p "$VENV/pipcache"
fi

pip --cache-dir="$VENV/pipcache"