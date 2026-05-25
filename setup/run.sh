#!/bin/bash

export VENV="${HOME}/goinfre/venv"
export CACHE="${HOME}/goinfre/.cache"
export UV_CACHE_DIR="${CACHE}/uv"
export HF_HOME="${CACHE}/hf"

export UV_PROJECT_ENVIRONMENT="${VENV}"

uv run python -m srcs \
    --active \
    --functions_definition data/input/functions_definition.json \
    --input data/input/function_calling_tests.json \
    --output data/output/function_calls.json
