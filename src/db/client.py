from motor.motor_asyncio import AsyncIOMotorClient

from src.config.settings import get_settings


class MongoDBClient:
    def __init__(self):
        settings = get_settings()

        self.client = AsyncIOMotorClient(settings.mongo_uri)
        self.database = self.client[settings.mongo_db_name]

    def get_collection(self, collection_name: str):
        return self.database[collection_name]

    async def close(self):
        self.client.close()


mongo_client = MongoDBClient()