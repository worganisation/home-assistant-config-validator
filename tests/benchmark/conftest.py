"""Isolated copies of the checked-out HA release for benchmark tests."""

from __future__ import annotations

import shutil
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING, Final
from unittest.mock import patch
from uuid import uuid4

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

TMP_DIR: Final[Path] = Path.cwd() / f".tmp_{uuid4()}"


@pytest.fixture(scope="session", autouse=True)
def _benchmark_workspace() -> Generator[None, None, None]:
    TMP_DIR.mkdir()

    try:
        yield
    finally:
        shutil.rmtree(TMP_DIR)


@pytest.fixture(name="clean_repo")
def clean_repo_() -> Generator[Path, None, None]:
    """Copy the HA checkout so each benchmark can modify its own fixture."""
    source = Path(environ["HA_BENCHMARK_REPO_PATH"])
    repo_path = TMP_DIR / "home-assistant"
    shutil.copytree(source, repo_path, ignore=shutil.ignore_patterns(".git"))

    try:
        with patch.dict(environ, {"HA_REPO_PATH": str(repo_path)}):
            yield repo_path
    finally:
        shutil.rmtree(repo_path)
