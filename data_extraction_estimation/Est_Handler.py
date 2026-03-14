from data_extraction_estimation.Estimation_Search import get_item_values
# from data_extraction_estimation.Label_Extraction import Label_Extraction
import time

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

    file_path = "international_fooditems.txt"

    # Load items from text file
    with open(file_path, "r", encoding="utf-8") as f:
        o1 = [line.strip() for line in f if line.strip()]

    print(o1)
    o2 = []

    total_time = 0
    found = 0
    not_found = 0

    for i in o1:
        start = time.time()

        result = Est_Handler(i, "image")

        end = time.time()

        elapsed = end - start
        total_time += elapsed

        o2.append(result)

        # simple found / not found check
        if result:
            found += 1
        else:
            not_found += 1

    avg_time = total_time / len(o1) if o1 else 0

    print("\n------ RESULTS ------")
    print(f"Total items checked: {len(o1)}")
    print(f"Items found: {found}")
    print(f"Items not found: {not_found}")
    print(f"Average search time: {avg_time:.3f} seconds")