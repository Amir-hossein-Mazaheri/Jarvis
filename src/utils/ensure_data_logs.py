from os import getcwd, path
from aiofiles import os, open

from src.constants.other import ADMIN_DATA_FILE, DATA_DIR_PATH


async def ensure_data_logs():
    """
    Just makes sure that data directory and data logs files exist if not creates them
    """
    data_dir_path = path.join(getcwd(), DATA_DIR_PATH)
    admin_data_file_path = path.join(
        getcwd(), DATA_DIR_PATH, ADMIN_DATA_FILE)

    if not path.isdir(data_dir_path):
        await os.mkdir(data_dir_path)

    if not path.isfile(admin_data_file_path):
        (await open(admin_data_file_path, 'x')).close()
