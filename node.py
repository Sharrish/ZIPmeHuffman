class Node:
    """
    A class for nodes when building a tree in the Huffman algorithm.
    """

    def __init__(self, key=None, value=0, left=None, right=None):
        self.key = key
        self.value = value
        self.left = left   # left child Node
        self.right = right # right child Node

    def __gt__(self, other):
        """Defining the great operator."""
        return self.value > other.value

    def __lt__(self, other):
        """Defining the less operator."""
        return self.value < other.value

    def __ge__(self, other):
        """Defining the great and equal operator."""
        return self.value >= other.value

    def __le__(self, other):
        """Defining the less and equal operator."""
        return self.value <= other.value





