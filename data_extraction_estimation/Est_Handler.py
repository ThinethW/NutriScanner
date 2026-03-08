from data_extraction_estimation.Estimation_Search import get_item_values
# from data_extraction_estimation.Label_Extraction import Label_Extraction

def Est_Handler(data: str, iType: str) -> tuple | None:
    """
    Main function for the module
    Handles Image and label extraction
    """
    if iType == "image":
        print("search")
        return get_item_values(data)
    if iType == "label":
        pass
        # return Label_Extraction.get_label_info(data)
    return None


if __name__ == "__main__":
    tests = (
        "Yogurt, plain, low fat",
        "Fried Rice"
    )

    for i, test in enumerate(tests, 1):
        print(f"check {i}: {test}:\t\t{Est_Handler(test, 'image')}")
