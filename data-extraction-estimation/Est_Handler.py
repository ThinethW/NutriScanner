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
    print(f"check 1: Yogurt, plain, low fat:\t\t{Est_Handler("Yogurt, plain, low fat", "image")}")
    print(f"check 2: Yogurt, plain, low fat:\t\t{Est_Handler("Yogurt", "image")}")
    print(f"check 3: sesame chicken:\t\t{Est_Handler("sesame chicken", "image")}")
    print(f"check 4: sesame chicken:\t\t{Est_Handler("sesame chicken", "image")}")
    print(f"check 5: Restaurant, Chinese, fried rice, without meat:\t\t{Est_Handler("Restaurant, Chinese, fried rice, without meat", "image")}")
    print(f"check 6: fried rice:\t\t{Est_Handler("fried rice", "image")}")
