import csv
import Logger
from objects import fooditem


def create_food_object(row):
    """
    Creates a fooditem object from a CSV row.

    Args:
        row: CSV row containing [id, name, calories, proteins, fats, carbohydrates,
             sodium, magnesium, calcium, iron, zinc, vitamin_a, vitamin_b, vitamin_c,
             vitamin_d, vitamin_e, vitamin_k, vitamin_b1, vitamin_b2, vitamin_b3,
             vitamin_b6, vitamin_b12, tally]

    Returns:
        fooditem: Food object with name, nutritional, and tally attributes
    """
    name = row[1]

    nutritional = {
        "calories": float(row[2]) if row[2] else -1,
        "proteins": float(row[3]) if row[3] else -1,
        "fats": float(row[4]) if row[4] else -1,
        "carbohydrates": float(row[5]) if row[5] else -1,
        "sodium": float(row[6]) if row[6] else -1,
        "magnesium": float(row[7]) if row[7] else -1,
        "calcium": float(row[8]) if row[8] else -1,
        "iron": float(row[9]) if row[9] else -1,
        "zinc": float(row[10]) if row[10] else -1,
        "vitamin_a": float(row[11]) if row[11] else -1,
        "vitamin_b": float(row[12]) if row[12] else -1,
        "vitamin_c": float(row[13]) if row[13] else -1,
        "vitamin_d": float(row[14]) if row[14] else -1,
        "vitamin_e": float(row[15]) if row[15] else -1,
        "vitamin_k": float(row[16]) if row[16] else -1,
        "vitamin_b1": float(row[17]) if row[17] else -1,
        "vitamin_b2": float(row[18]) if row[18] else -1,
        "vitamin_b3": float(row[19]) if row[19] else -1,
        "vitamin_b6": float(row[20]) if row[20] else -1,
        "vitamin_b12": float(row[21]) if row[21] else -1,
    }

    tally = int(row[22]) if len(row) > 22 and row[22] else 0

    return fooditem(name, nutritional, tally)


def Estimation_Search(data, logger):
    """
    Searches through multiple datasets to find nutritional information for a food item.

    Args:
        data: List where data[0] is the food name to search for
        logger: Logger object for error reporting

    Returns:
        dict: Food object if found, None otherwise
    """
    search_functions = [
        lambda: search_frequented(data),
        lambda: search_NutriScannerDB(data),
        lambda: search_IRD(data),
        lambda: search_Fastfood(data),
        lambda: search_External(data),
        lambda: search_USDA(data)
    ]

    for search_func in search_functions:
        values = search_func()
        if values is not None:
            return values

    # If not found in any dataset, try ontology search
    values = Ontology_link_and_search(data, logger)
    if values is not None:
        return values

    logger.log("ERROR: No data found in DB")
    return None


def search_frequented(data):
    """Search the user's frequently scanned foods."""
    try:
        with open("module_2_datasets/frequented_foods.csv", "r") as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None)  # Skip header if present
            for row in csv_reader:
                if len(row) > 1 and row[1].lower() == data[0].lower():
                    return create_food_object(row)
    except FileNotFoundError:
        pass
    return None


def search_NutriScannerDB(data):
    """Search the NutriScanner global database."""
    try:
        with open("module_2_datasets/NutriScannerDB.csv", "r") as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None)  # Skip header if present
            for row in csv_reader:
                if len(row) > 1 and row[1].lower() == data[0].lower():
                    return create_food_object(row)
    except FileNotFoundError:
        pass
    return None


def search_IRD(data):
    """Search the IRD dataset."""
    try:
        with open("module_2_datasets/IRD.csv", "r") as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None)  # Skip header if present
            for row in csv_reader:
                if len(row) > 1 and row[1].lower() == data[0].lower():
                    return create_food_object(row)
    except FileNotFoundError:
        pass
    return None


def search_Fastfood(data):
    """Search the Fastfood dataset."""
    try:
        with open("module_2_datasets/Fastfood.csv", "r") as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None)  # Skip header if present
            for row in csv_reader:
                if len(row) > 1 and row[1].lower() == data[0].lower():
                    return create_food_object(row)
    except FileNotFoundError:
        pass
    return None


def search_External(data):
    """Search external files dataset."""
    try:
        with open("module_2_datasets/External.csv", "r") as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None)  # Skip header if present
            for row in csv_reader:
                if len(row) > 1 and row[1].lower() == data[0].lower():
                    return create_food_object(row)
    except FileNotFoundError:
        pass
    return None


def search_USDA(data):
    """Search the USDA dataset (largest, searched last)."""
    try:
        with open("module_2_datasets/USDA.csv", "r") as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None)  # Skip header if present
            for row in csv_reader:
                if len(row) > 1 and row[1].lower() == data[0].lower():
                    return create_food_object(row)
    except FileNotFoundError:
        pass
    return None


def Ontology_link_and_search():
    pass


def Append_frequented_foods():
    pass


def Append_NutriScannerDB():
    pass
