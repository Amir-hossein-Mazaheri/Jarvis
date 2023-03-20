from prisma import Prisma
import logging

db = Prisma()


async def connect_to_db(_):
    await db.connect()
    logging.info("\n\nSuccessfully connected to database...\n")
