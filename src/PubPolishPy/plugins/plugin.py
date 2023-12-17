from abc import ABC, abstractmethod

class PubPolishPlugin(ABC):
    def __init__(self, formatter):
        self.formatter = formatter

    @abstractmethod
    def pre_migrate(self):
        pass

    @abstractmethod
    def post_migrate(self):
        pass


