import Logger
import Estimation_Search
import Label_Extraction


class Est_Handler:
    def __init__(self):
        self.data = None
        self.Logger = Logger.Logger("data-extraction-estimation")

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def dataSelection(self):
        # initial check
        if self.data == "" or self.data is None:
            self.Logger.log("ERROR: No data selected")
            return
        else:

            # type selection
            if type(self.data) == str:
                self.Logger.log("INFO: Data selected: OCR Data")

            if type(self.data) == tuple:
                self.Logger.log("INFO: Data selected: Selection")
