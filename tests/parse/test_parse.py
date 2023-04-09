import asyncio
import os
import pytest

from aiohttp.web_exceptions import HTTPError
from parse_script.main import open_page, save_data, clear, calc_hash, get_path, find_link, run_workers


async def test_assess(file_paths, workers):
    """Проверяет, что при удачном подключении возвращается количество ссылок равное количеству воркеров."""
    assert len(file_paths) == workers


async def test_http_error():
    """Проверяет обработку исключения, если код != 200."""
    path = "https://gitea.radium.group/radium/project-configuration"
    with pytest.raises(HTTPError):
        await open_page(path, 400)


async def test_no_link(response):
    """Проверяет обработку исключения, если ссылки для скачивания не найдены."""
    with pytest.raises(KeyError):
        await find_link(response)


async def test_extracting(file_paths, workers):
    """Проверяет, что файлы скачались и директорий создано по кол-ву воркеров."""
    for num, file_p in enumerate(file_paths):
        await save_data(num, file_p)
    temp_dirs = [f"temp{i}" for i in range(workers) if f"temp{i}" in os.listdir("./")]
    assert len(temp_dirs) == workers


async def test_get_path(dirs, workers):
    """Проверяет, что функция находит все вложенные файлы во временных директориях."""
    for num in range(workers):
        for direct in os.listdir("./"):
            if "temp" in direct:
                check_dirs = get_path(direct)
        assert len(check_dirs) == len(dirs)


async def test_calc_hash(dirs, hash_s, workers):
    """Проверяет подсчет хэша."""
    new_hash = {}
    for num in range(workers):
        for unit, filepath in dirs.items():
            new_hash[unit] = calc_hash(filepath, unit, num)
        assert new_hash == hash_s


async def test_clear_temp_dirs(workers):
    """Проверяет, что директории удаляются после подсчета хэша."""
    clear()
    temp_dirs = [f"temp{i}" for i in range(workers) if f"temp{i}" in os.listdir("./")]
    assert not temp_dirs


def test_run_workers(workers):
    """Проверяет общую работу раннера - запуск и создание директорий."""
    path = "https://gitea.radium.group/radium/project-configuration"
    asyncio.run(run_workers(workers, path))
    count_temp = [elem for elem in os.listdir("./") if "temp" in elem]
    assert len(count_temp) == workers
    clear()
