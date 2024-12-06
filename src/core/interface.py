# structeng/interfaces.py
from abc import ABC, abstractmethod

class WebServiceInterface(ABC):
    @abstractmethod
    def create_section(self, data: dict):
        pass

    @abstractmethod
    def calculate_properties(self, section_id: str):
        pass