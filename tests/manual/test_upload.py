from src.storage.blob_client import azure_blob_client

blob_url = azure_blob_client.upload_file(
    r"/Users/amith2831/Desktop/ML INTERNSHIP/0 LIBRARIES/2 PANDAS/data.csv",
    "test/data.csv"
)

print(blob_url)