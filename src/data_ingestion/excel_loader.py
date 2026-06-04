import pandas as pd
from src.data_ingestion.base_loader import BaseLoader


class XLSXLoader(BaseLoader):
    def load_data(self, file_path: str) -> pd.DataFrame:
        try:
            data = pd.read_excel(file_path)
        except Exception as e:
            raise ValueError(f"Failed to load Excel file: {file_path}") from e

        if data.empty:
            raise ValueError("Uploaded Excel file is empty")

        return data