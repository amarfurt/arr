"""
Task base class.
"""

from abc import ABC, abstractmethod


class Task(ABC):

    @abstractmethod
    def add_parser(self, registry):
        """ Add a parser for this task. """
        pass

    @abstractmethod
    def run(self, args):
        """ Run the task. """
        pass
