from csDetector import CsDetector
# this is the adapter class. we can use it call the adaptee from different sources of input
# by inheriting csDetector, it will call the executeTool method with the right parameters but it will gather
# input by the web service


class CsDetectorAdapter(CsDetector):
    def detectSmells(gitRepository, gitPAT, startingDate="default", sentiFolder="./senti", outputFolder="./out"):
        if(startingDate == default):
            # in this branch we execute the tool normally because no date was provided
            CsDetector().executeTool(
                ['-p', gitPAT, '-r', gitRepository, '-s', sentiFolder, '-o', outFolder])
            return
        else:
            # if a date is specified we have to execute with one more parameter
            CsDetector().executeTool(['-p', gitPAT, '-r', gitRepository,
                                      '-s', sentiFolder, '-o', outFolder, '-sd', startingDate])
            return
