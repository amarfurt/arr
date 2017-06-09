"""
Task base class.
"""

from abc import ABC, abstractmethod


class Task(ABC):

    @staticmethod
    @abstractmethod
    def add_parser(registry):
        """ Add a parser for this task. """
        pass

    def __init__(self, server):
        self.server = server

    @abstractmethod
    def run(self, args):
        """ Run the task. """
        pass
