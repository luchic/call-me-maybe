
install:
	bash setup/install.sh

run:
	bash setup/run.sh


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
