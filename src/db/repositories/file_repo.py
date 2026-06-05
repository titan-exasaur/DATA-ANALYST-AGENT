from src.db.client import mongo_client
from src.db.models import FileMetadata


class FileRepository:
    def __init__(self):
        self.collection = mongo_client.get_collection("files")

    async def create_file(self, file_metadata: FileMetadata):
        document = file_metadata.model_dump()
        await self.collection.insert_one(document)
        return document

    async def get_file_by_id(self, file_id: str):
        return await self.collection.find_one({"file_id": file_id})