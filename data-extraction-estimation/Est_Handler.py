import Estimation_Search
import Label_Extraction
import Logger


def Est_Handler(data: str, iType: str) -> tuple:
    """
    Main function for the module
    Handles Image and label extraction
    """
    if iType == "image":
        print("search")
        return Estimation_Search.get_item_values(data)
    if iType == "label":
        return Label_Extraction.get_label_info(data)

if __name__ == "__main__":
    print(*Est_Handler("sesame Restaurant chicken Chinese", "image"))
