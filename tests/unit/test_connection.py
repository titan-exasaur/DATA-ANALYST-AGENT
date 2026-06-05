# tests/test_mongo_connection.py

import asyncio

from src.db.client import mongo_client


async def main():
    collections = await mongo_client.database.list_collection_names()

    print("Connected successfully")
    print(collections)


asyncio.run(main())