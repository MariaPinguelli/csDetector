from devNetwork import devNetwork
from typing import Sequence
import sys
import os

# Adaptee class for the adapter pattern, the one responsible for the execution of the tool (through the executeTool method)
# since the target takes command line input, but we want to send data in json from a web service, we need an adapter to fix the problem


class CsDetector:

    def executeTool(self, argv):
        devNetwork(argv)


if __name__ == "__main__":
    tool = CsDetector()
    tool.executeTool(sys.argv[1:])
