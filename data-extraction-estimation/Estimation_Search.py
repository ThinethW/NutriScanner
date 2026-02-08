import csv
import Logger


def Estimation_Search(data, logger):
    values = None
    funcs = [search_frequented(data), search_NutriScannerDB(), search_IRD(), search_Fastfood(), search_External(), search_USDA()]
    for func in funcs:
        values = func
        if values is None:
            break
    if values is not None:
        pass
    else:
        logger.log("ERROR: No data found in DB")
    return values


def search_frequented(data):
    file = open("module_2_datasets/frequented_foods.csv", "r")
    ct = 1
    for row in csv.reader(file):
        if row[ct] == data[0]:
            return row[ct]
    else:
        pass


def search_NutriScannerDB():
    pass


def search_IRD():
    pass


def search_External():
    pass


def search_Fastfood():
    pass


def search_USDA():
    pass


def Ontology_link_and_search():
    pass


def Append_frequented_foods():
    pass


def Append_NutriScannerDB():
    pass
