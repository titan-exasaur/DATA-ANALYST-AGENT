from abc import ABC, abstractmethod
import pandas as pd


class BaseLoader(ABC):
    @abstractmethod
    def load(self, source: str) -> pd.DataFrame:
        """
        Load data from a given file path.

        Args:
            source: source of data

        Returns:
            pd.DataFrame
        """
        pass