class fooditem():
    """
    this is used to load food item data from the dataset, it contains the food items...
    name: str,
    nutritional info: dict,
    tally: int
    """

    def __init__(self, name: str, nutritional: dict, tally: int):
        self.name = name
        self.nutritional = nutritional
        self.tally = tally

    def get_by_name(self):
        return self
