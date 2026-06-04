import pandas as pd
import requests
from urllib.parse import urlparse


class URLLoader:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def _is_valid_url(self, url: str) -> bool:
        parsed_url = urlparse(url)

        return (
            parsed_url.scheme in ["http", "https"]
            and parsed_url.netloc != ""
        )

    def _check_url_accessible(self, url: str) -> None:
        try:
            response = requests.head(
                url,
                timeout=self.timeout,
                allow_redirects=True
            )

            if response.status_code >= 400:
                raise ValueError(
                    f"URL is not accessible. Status code: {response.status_code}"
                )

        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to URL: {url}") from e

    def load_data(self, url: str) -> pd.DataFrame:
        """
        Loads CSV data from a given URL.

        Args:
            url: HTTP/HTTPS URL pointing to a CSV file.

        Returns:
            pd.DataFrame: Loaded dataset.
        """

        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")

        self._check_url_accessible(url)

        try:
            url_data = pd.read_csv(url)
        except Exception as e:
            raise ValueError(f"Failed to load CSV data from URL: {url}") from e

        if url_data.empty:
            raise ValueError("Loaded dataset is empty")

        print(
            f"Loaded dataset from URL: "
            f"{url_data.shape[0]} rows × {url_data.shape[1]} columns"
        )

        return url_data