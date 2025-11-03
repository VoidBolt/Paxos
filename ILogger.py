from abc import ABC, abstractmethod

class ILogger(ABC):
    """Interface-like abstract base class for custom loggers."""

    @abstractmethod
    def log(self, level, msg, **kwargs):
        pass

    @abstractmethod
    def debug(self, msg, **kwargs):
        pass

    @abstractmethod
    def info(self, msg, **kwargs):
        pass

    @abstractmethod
    def warning(self, msg, **kwargs):
        pass

    @abstractmethod
    def error(self, msg, **kwargs):
        pass

    @abstractmethod
    def critical(self, msg, **kwargs):
        pass

