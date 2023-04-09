import asyncio
import os
import pytest
from aiohttp import ClientSession
from parse_script.main import open_page, get_path, calc_hash


@pytest.fixture(autouse=True)
async def session():
    return ClientSession()


@pytest.fixture(autouse=True)
async def session():
    return ClientSession()


@pytest.fixture(autouse=True)
async def response(session):
    path = "https://example.com"
    async with session as session:
        resp = await session.get(path)
        return resp


@pytest.fixture
async def workers():
    count_workers = 4
    return count_workers


@pytest.fixture
async def file_paths(workers):
    path = "https://gitea.radium.group/radium/project-configuration"
    runners = await asyncio.gather(*[open_page(path) for _ in range(workers)])
    return runners


@pytest.fixture
async def dirs():
    for direct in os.listdir("./"):
        if "temp" in direct:
            dict_dirs = get_path(direct)
            return dict_dirs


@pytest.fixture
async def hash_s(dirs):
    hash_files = {}
    for unit, filepath in dirs.items():
        hash_files[unit] = calc_hash(filepath, unit, filepath[4])
    return hash_files


@pytest.fixture(autouse=True, scope="function")
async def clear_files():
    yield
    for elem in os.listdir("./"):
        if "hash" in elem:
            os.remove(f"./{elem}")
