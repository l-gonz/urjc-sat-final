from abc import ABC, abstractmethod


class FeedParser(ABC):
    """
    Base class to make parsers for the Feed and Item models
    """

    @abstractmethod
    def __init__(self, stream):
        """
        Parameters
        ----------
        stream : HttpResponse
            The data to parse
        """
        pass

    @abstractmethod
    def feed_title(self):
        """Returns a string with the title of the feed."""
        pass

    @abstractmethod
    def items_data(self):
        """
        Returns a list of dictionaries with entries matching the fields
        in the Item model: key, title, description, picture

        Description picture is optional
        """
        pass

class ParsingError(RuntimeError):
    pass