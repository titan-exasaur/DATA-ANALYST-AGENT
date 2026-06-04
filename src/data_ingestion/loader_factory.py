from pathlib import Path

from src.data_ingestion.csv_loader import CSVLoader
from src.data_ingestion.excel_loader import XLSXLoader
from src.data_ingestion.validator import FileValidator


def load_uploaded_file(source: str):
    validator = FileValidator()
    validator.validate_file(source)

    extension = Path(source).suffix.lower()

    if extension == ".csv":
        loader = CSVLoader()
    elif extension == (".xlsx", ".xls"):
        loader = XLSXLoader()
    else:
        raise ValueError(f"Unsupported file type: {extension}")

    return loader.load(source)