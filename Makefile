install:
	uv sync --all-groups

update:
	uv lock --upgrade

test:
	@uv run pytest

try-repo:
	git add . && cd ../home-assistant && git add . && prek try-repo ../home-assistant-config-validator

include .env
export

vscode-shortcut-1:
	make try-repo

vscode-shortcut-2:
	uv run python home_assistant_config_validator/readme_generator.py

vscode-shortcut-3:
	uv run python home_assistant_config_validator/validate_entities.py

vscode-shortcut-4:
	uv run python home_assistant_config_validator/validate_lovelace.py
