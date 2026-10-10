# Home Assistant Config Validator

[![CodSpeed Badge](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/worgarside/home-assistant-config-validator)

Use Python 3.12 or later and `uv sync --locked --all-groups` to install the project and development dependencies. Run unit tests with `uv run pytest`; benchmarks use a Home Assistant release checkout supplied through `HA_BENCHMARK_REPO_PATH` and run separately with `uv run pytest tests/benchmark --codspeed -n 0`.

Install the Git hooks with `prek install`. Release creation uses the manual Semantic Release workflow on `main`.
