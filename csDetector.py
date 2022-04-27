from devNetwork import devNetwork
from typing import Sequence
import sys
import os


# since the interface of the execution is only command line input, we want something to adapt our web service
# we will have an adapter class that will extend csDetector and parses the local input

class CsDetector:

    # executeTool takes input like the following:
    # ['-p', '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', '-r', 'https://github.com/tensorflow/ranking', '-s', './senti', '-o', './out', (optional)'-sd', (optional)'2021-12-31']
    def executeTool(self, argv):
        devNetwork(argv)


if __name__ == "__main__":

    inputData = sys.argv[1:]
    tool = CsDetector()
    tool.executeTool(inputData)
