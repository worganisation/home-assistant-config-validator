"""Fixtures for the benchmark tests."""

from __future__ import annotations

import asyncio
import shutil
from contextlib import suppress
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING, Final
from unittest.mock import patch
from uuid import uuid4
from zipfile import ZipFile

import pytest
from aiohttp import ClientSession

if TYPE_CHECKING:
    from collections.abc import Generator

REPO_URL: Final[str] = (
    "https://api.github.com/repos/worganisation/home-assistant/releases/latest"
)

TMP_DIR: Final[Path] = Path.cwd() / f".tmp_{uuid4()}"
OUTPUT_ZIP: Final[Path] = TMP_DIR / "repo.zip"


async def _download_release() -> None:
    async with ClientSession(raise_for_status=True) as session:
        async with session.get(REPO_URL) as response:
            latest_release = await response.json()

        async with session.get(latest_release["zipball_url"]) as response:
            with OUTPUT_ZIP.open("wb") as output:
                async for chunk in response.content.iter_chunked(65536):
                    output.write(chunk)


@pytest.fixture(scope="session", autouse=True)
def _download_latest_release_zip() -> Generator[None, None, None]:
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
    TMP_DIR.mkdir(exist_ok=True)

    asyncio.run(_download_release())

    yield

    # Clean up
    shutil.rmtree(TMP_DIR)


@pytest.fixture(name="clean_repo")
def clean_repo_() -> Generator[Path, None, None]:
    """Extract the downloaded zip file and set the `HA_REPO_PATH` environment variable.

    Clean up the extracted repo after the test.
    """
    with ZipFile(OUTPUT_ZIP, "r") as zip_ref:
        zip_ref.extractall(TMP_DIR)

    repo_path = TMP_DIR / zip_ref.namelist()[0]

    with patch.dict(environ, {"HA_REPO_PATH": str(repo_path)}):
        yield repo_path

    with suppress(FileNotFoundError):
        shutil.rmtree(repo_path)
