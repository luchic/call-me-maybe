export VENV="${HOME}/goinfre/venv"
export CACHE="${HOME}/goinfre/.cache"
export UV_CACHE_DIR="${CACHE}/uv"
export HF_HOME="${CACHE}/hf"

export UV_PROJECT_ENVIRONMENT="${VENV}"

mkdir -p "$UV_CACHE_DIR" "$HF_HOME" "$VENV"
uv sync --python 3.11
