import Estimation_Search
import Label_Extraction
import Logger


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
            values = None
            # type selection
            if type(self.data) == str:
                self.Logger.log("INFO: Data selected: OCR Data")
                values = Label_Extraction.Label_Extraction(self.data)
                self.Logger.log(f"INFO: values returned \n{values}")

            elif type(self.data) == tuple:
                self.Logger.log("INFO: Data selected: Image")
                values = Estimation_Search.Estimation_Search(self.data)
                self.Logger.log(f"INFO: values returned \n{values}")
            else:
                self.Logger.log("ERROR: Not expected Datatype")
                values = None
            return values