import pandas as pd
from src.data_ingestion.base_loader import BaseLoader


class CSVLoader(BaseLoader):
    def load(self, source: str) -> pd.DataFrame:
        try:
            data = pd.read_csv(source)
        except Exception as e:
            raise ValueError(f"Failed to load CSV file: {source}") from e

        if data.empty:
            raise ValueError("Uploaded CSV file is empty")

        return data