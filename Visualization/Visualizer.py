from abc import abstractmethod


class Visualizer:

    @abstractmethod
    def draw(self, fig, height):
        pass
