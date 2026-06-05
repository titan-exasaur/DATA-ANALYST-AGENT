from pathlib import Path
from typing import Optional

from azure.storage.blob import BlobServiceClient, ContentSettings

from src.config.settings import get_settings


class AzureBlobClient:
    def __init__(self):
        settings = get_settings()

        self.connection_string = settings.azure_storage_connection_string
        self.container_name = settings.azure_storage_container_name

        if self.connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            self.container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
        else:
            self.blob_service_client = None
            self.container_client = None

    def is_enabled(self) -> bool:
        return self.container_client is not None

    def upload_file(self, file_path: str, blob_name: str) -> Optional[str]:
        if not self.is_enabled():
            return None

        path = Path(file_path)

        content_type = "application/octet-stream"
        if path.suffix.lower() == ".csv":
            content_type = "text/csv"
        elif path.suffix.lower() in [".xlsx", ".xls"]:
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        blob_client = self.container_client.get_blob_client(blob_name)

        with open(file_path, "rb") as file:
            blob_client.upload_blob(
                file,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type),
            )

        return blob_client.url


azure_blob_client = AzureBlobClient()