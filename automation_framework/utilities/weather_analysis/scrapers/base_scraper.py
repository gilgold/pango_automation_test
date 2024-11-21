from abc import ABC, abstractmethod
from typing import Optional


class Scraper(ABC):
    @abstractmethod
    def get_temperature(self, city: str) -> Optional[float]:
        pass

    @abstractmethod
    def close(self):
        pass