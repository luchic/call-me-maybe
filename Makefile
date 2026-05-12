
install:
	bash setup/install.sh

run:
	uv run python -m src \
		--functions_definition data/input/functions_definition.json \
		--input data/input/function_calling_tests.json \
		--output data/output/function_calls.json


clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -name .pytest_cache -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

fclean: clean
	rm -rf "$(HOME)/goinfre/.cache/"
	rm -rf "$(HOME)/goinfre/venv/"

.PHONY: install run debug clean fclean
