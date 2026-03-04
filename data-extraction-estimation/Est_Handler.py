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
    tests = (
        "Yogurt, plain, low fat",
        "Yogurt",
        "chicken",
        "sesame chicken",
        "Restaurant, Chinese, fried rice, without meat",
        "fried rice",
        "curry",
    )

    for i, test in enumerate(tests, 1):
        print(f"check {i}: {test}:\t\t{Est_Handler(test, 'image')}")
