export CACHE="${HOME}/goinfre/.cache"
export UV_CACHE_DIR="${CACHE}/uv"
export HF_HOME="${CACHE}/hf"

mkdir -p "$UV_CACHE_DIR" "$HF_HOME"
uv sync --python 3.11
