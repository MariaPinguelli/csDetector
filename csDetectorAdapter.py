from csDetector import CsDetector
import os
import argparse
from typing import Sequence
# this is the adapter class. we can use it to call the adaptee from different sources of input
# by inheriting csDetector, we override the method with bad specicied interface with a better
# one that will call the superclass method after parsing the given input


class CsDetectorAdapter(CsDetector):
    def __init__(self):
        super().__init__()

    def executeTool(self, gitRepository, gitPAT, startingDate="default", sentiFolder="./senti", outputFolder="./out"):

        if(startingDate == "default"):
            # in this branch we execute the tool normally because no date was provided
            super().executeTool(
                ["-p", gitPAT, "-r", gitRepository, "-s", sentiFolder, "-o", outputFolder])
            return
        else:
            # if a date is specified we have to execute with one more parameter
            super().executeTool(['-p', gitPAT, '-r', gitRepository,
                                 '-s', sentiFolder, '-o', outFolder, '-sd', startingDate])
            return


if __name__ == "__main__":

    tool = CsDetectorAdapter()
    tool.executeTool("https://github.com/tensorflow/ranking",
                     "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")
