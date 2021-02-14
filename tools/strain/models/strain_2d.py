from abc import ABC, abstractmethod

class Strain_2d(ABC):
    """
    Implement a generic 2D strain rate method
    """
    def __init__(self):
        # Initialize general parameters
        self._Name = None
        self._velfield = None
        self._params = None

    def __str__(self):
        # print method
        raise NotImplementedError

    def Method(self):
        return self._Name

    def write(self):
        # Write results to files
        raise NotImplementedError

    @abstractmethod
    def compute(self, myVelfield, MyParams):
        # generic method to be implemented in each method
        pass