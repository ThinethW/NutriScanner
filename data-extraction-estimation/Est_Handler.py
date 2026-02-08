import Estimation_Search
import Label_Extraction
import Logger


class Est_Handler:
    """
    this is the general handler for this module.

    data contains 2 possible input types that define whether or not it is a label or an image:
    string: label
    list: image (the list contains tuples consisting of the item name and quantity... (name, quantity))
    """

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

            elif type(self.data) == list:
                for i in self.data:
                    if type(i) == tuple:
                        self.Logger.log(f"INFO: Data selected: Image\t\tselected: {i}")
                        values = Estimation_Search.Estimation_Search(self.data, logger=self.Logger)
                        self.Logger.log(f"INFO: values returned \n{values}")
                    else:
                        self.Logger.log(f"ERROR: Not expected Datatype: List did not contain tuple. contained {type(i)}")
            else:
                self.Logger.log("ERROR: Not expected Datatype. Layer 1")
                values = None
            return values
