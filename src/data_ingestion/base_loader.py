from abc import ABC, abstractmethod
import pandas as pd


class BaseLoader(ABC):
    @abstractmethod
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load data from a given file path.

        Args:
            file_path: Path to uploaded file.

        Returns:
            pd.DataFrame
        """
        pass