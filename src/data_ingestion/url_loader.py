import requests
import pandas as pd
from pathlib import Path
from urllib.parse import urlparse
from src.data_ingestion.base_loader import BaseLoader

class URLLoader(BaseLoader):
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def _is_valid_url(self, source: str) -> bool:
        parsed_url = urlparse(source)

        return (
            parsed_url.scheme in ["http", "https"]
            and parsed_url.netloc != ""
        )

    def _check_url_accessible(self, source: str) -> None:
        try:
            response = requests.head(
                source,
                timeout=self.timeout,
                allow_redirects=True
            )

            if response.status_code >= 400:
                raise ValueError(
                    f"URL is not accessible. Status code: {response.status_code}"
                )

        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to URL: {source}") from e

    def data(self, source: str) -> pd.DataFrame:
        """
        Loads CSV data from a given URL.

        Args:
            source: HTTP/HTTPS URL pointing to a CSV file.

        Returns:
            pd.DataFrame: Loaded dataset.
        """

        if not self._is_valid_url(source):
            raise ValueError(f"Invalid URL: {source}")

        self._check_url_accessible(source)

        ext = Path(urlparse(source).path).suffix.lower()
        try:
            if ext in (".xlsx", ".xls"):
                url_data = pd.read_excel(source)
            else:
                url_data = pd.read_csv(source)   # default to CSV
        except Exception as e:
            raise ValueError(f"Failed to load data from URL: {source}") from e

        if url_data.empty:
            raise ValueError("Loaded dataset is empty")

        print(
            f"Loaded dataset from URL: "
            f"{url_data.shape[0]} rows × {url_data.shape[1]} columns"
        )

        return url_data