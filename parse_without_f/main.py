"""Скрипт асинхронно скачивает содержимое \
HEAD репозитория https://gitea.radium.group/radium/project-configuration \
и вычисляет хэш всех файлов."""
import asyncio
import glob
import hashlib
import os
import shutil
import zipfile
from typing import Optional

import wget
from aiohttp import ClientResponse, ClientSession, TCPConnector
from aiohttp.web_exceptions import HTTPError
from bs4 import BeautifulSoup


async def find_link(resp: ClientResponse) -> Optional[str]:
    """Ищет ссылку для скачивания, если находит, возвращает ее."""
    soup = BeautifulSoup(await resp.text(), "html.parser")
    res = soup.find_all("div", class_="menu")
    for tag in res:
        res = tag.find("a")["href"]
        if ".zip" in res:
            return res
    raise KeyError("Required link not found")


async def open_page(path: str, ok_status: int = 200) -> Optional[str]:
    """
    Загружает страницу и ищет нужную ссылку с помощью find_link.

    Если находит, то передает save_data, чтобы скачать файлы.
    """
    async with ClientSession(connector=TCPConnector()) as session:
        async with session.get(path) as resp:
            if resp.status == ok_status:
                res = await find_link(resp)
                if res:
                    return res
            raise HTTPError(reason="No access to site, reason: {status}".format(status=resp.status))


async def save_data(worker: int, f_path: str) -> str:
    """Скачивает архив, распаковывает и удаляет его."""
    base_url = "https://gitea.radium.group"
    dir_path = "./temp{num}".format(num=worker)
    os.makedirs(dir_path, exist_ok=True)
    filename = "{base}{address}".format(base=base_url, address=f_path)
    wget.download(filename, out="file{num}".format(num=worker))
    with zipfile.ZipFile("file{num}".format(num=worker), "r") as archive:
        archive.extractall(dir_path)
    os.remove("./file{num}".format(num=worker))
    return filename


def get_path(path_to_file: str) -> dict:
    """Сохраняет пути до всех скачанных файлов."""
    dirs = {}
    for subdir, _dirs, files in os.walk(path_to_file):
        for elem in files:
            dirs[elem] = subdir + os.sep + elem
    return dirs


def calc_hash(path_to_file: str, elem: str, worker: int, block_size: int = 4096) -> str:
    """Считает хэш и сохраняет его в файл."""
    sha256_hash = hashlib.sha256()
    with open(path_to_file, "rb") as file_in:
        file_hash = iter(lambda: file_in.read(block_size), b"")
        for byte_block in file_hash:
            sha256_hash.update(byte_block)
    with open("hash_files_{num}.txt".format(num=worker), "a") as file_out:
        # можно сделать вывод в консоль, напр.: print(f"hash of file -> {file}: {sha256_hash.hexdigest()}")
        file_out.write("hash of file -> {elem}: {hash256}\n".format(elem=elem, hash256=sha256_hash.hexdigest()))
        return sha256_hash.hexdigest()


def clear() -> None:
    """Удаляет все файлы, после того как хэш подсчитан."""
    for directory in glob.glob("*/"):
        if "temp" in directory:
            shutil.rmtree(directory)


async def run_workers(workers: int, path: str) -> None:
    """Запускает задачи по кол-ву воркеров для скачивания файлов по ссылке."""
    tasks = [open_page(path) for _ in range(workers)]
    files = await asyncio.gather(*tasks)

    tasks_save = [save_data(num, f_path) for num, f_path in enumerate(files)]
    await asyncio.gather(*tasks_save)


if __name__ == "__main__":
    path_to = "https://gitea.radium.group/radium/project-configuration"
    count_workers = 3

    asyncio.run(run_workers(workers=count_workers, path=path_to))
    for _ in range(count_workers):
        paths = get_path("./temp{0}".format(_))
        for unit, filepath in paths.items():
            calc_hash(filepath, unit, _)
    clear()
