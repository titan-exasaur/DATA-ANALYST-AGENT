import pandas as pd
from src.data_ingestion.base_loader import BaseLoader


class XLSXLoader(BaseLoader):
    def data(self, source: str) -> pd.DataFrame:
        try:
            data = pd.read_excel(source)
        except Exception as e:
            raise ValueError(f"Failed to load Excel file: {source}") from e

        if data.empty:
            raise ValueError("Uploaded Excel file is empty")

        return data