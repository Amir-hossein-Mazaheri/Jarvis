import json
from os import path, getcwd
from aiofiles import open

from src.constants.other import DATA_DIR_PATH, ADMIN_DATA_FILE


async def get_enable_to_edit():
    admin_log_data_file_path = path.join(
        getcwd(), DATA_DIR_PATH, ADMIN_DATA_FILE)

    enable_to_edit = True

    async with open(admin_log_data_file_path, 'r') as handler:
        file = await handler.read()
        parsed_file = json.loads(file if file else "{}")

        if "enable_to_edit" in parsed_file:
            enable_to_edit = parsed_file["enable_to_edit"]

    return enable_to_edit
