import pandas as pd
from src.data_ingestion.base_loader import BaseLoader


class CSVLoader(BaseLoader):
    def load_data(self, file_path: str) -> pd.DataFrame:
        try:
            data = pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Failed to load CSV file: {file_path}") from e

        if data.empty:
            raise ValueError("Uploaded CSV file is empty")

        return data