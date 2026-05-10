from data_extraction_estimation.Estimation_Search import get_item_values

def main(data: str, iType: str) -> tuple | None:
    """
    Main function for the module
    Handles Image and label extraction
    """
    if iType == "image":
        print("search")
        return get_item_values(data)
    if iType == "label":
        pass
    return None


if __name__ == "__main__":
    items = []
    results = []
    notFound = []

    with open("test.txt", "r") as file:
        for line in file:
            items.append(line.strip())

    print(items)

    for i in items:
        result = main(i, "image")

        if result == ():  # check for empty tuple
            notFound.append(i)
        else:
            results.append(result)

    print("DONE\n")

    print("Results:")
    for r in results:
        print(r)

    print("\nNot Found:")
    for n in notFound:
        print(n)