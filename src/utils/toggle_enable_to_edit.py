import json
from os import path, getcwd
from aiofiles import open

from src.constants.other import DATA_DIR_PATH, ADMIN_DATA_FILE


async def toggle_enable_to_edit():
    admin_log_data_file_path = path.join(
        getcwd(), DATA_DIR_PATH, ADMIN_DATA_FILE)

    async with open(admin_log_data_file_path, 'rb+') as handler:
        file = await handler.read()
        parsed_file = json.loads(file if file else "{}")

        content = {"enable_to_edit": not parsed_file["enable_to_edit"]
                   if "enable_to_edit" in parsed_file else False}

        await handler.seek(0)
        await handler.truncate()

        await handler.write(bytes(json.dumps(content), 'utf-8'))
