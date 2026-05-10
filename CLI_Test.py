import model1
from data_extraction_estimation import Est_Handler, Est_Handler, Label_Extraction
import nutritional_analysis.analyzer_refac as a


def mo2_Parse(nutrients):
    # test
    return {
        "Energy (kcal)": float(nutrients[1]),
        "Total meal weight (g)": 100,
        "Carbohydrates digestible (g)": float(nutrients[4]),
        "Total fiber (g)": float(nutrients[6]),
        "Protein (g)": float(nutrients[2]),
        "Sodium": float(nutrients[5]),
        "SFA": float(nutrients[20]),
        "MUFA": float(nutrients[21]),
        "PUFA": float(nutrients[22]),
    }

def mo4_Parse(nutrients):
    DEFAULTS = {
        "Daily_Calories_kcal": 0.0,
        "Carbohydrates_g": 0.0,
        "Protein_g": 0.0,
        "Total_Fat_g": 0.0,
        "Saturated_Fat_g": 0.0,
        "Trans_Fat_g": 0.0,
        "Total_Sugar_g": 0.0,
        "Added_Sugar_g": 0.0,
        "Fiber_g": 0.0,
        "Sodium_mg": 0.0,
        "Potassium_mg": 0.0,
        "Calcium_mg": 0.0,
        "Iron_mg": 0.0,
        "Vitamin_D_IU": 0.0,
        "Vitamin_B12_mcg": 0.0,
        # extras from input that map cleanly
        "Magnesium_mg": 0.0,
        "Zinc_mg": 0.0,
        "Vitamin_A_mcg": 0.0,
        "Vitamin_C_mg": 0.0,
        "Vitamin_E_mg": 0.0,
        "Vitamin_K_mcg": 0.0,
        "Vitamin_B1_mg": 0.0,
        "Vitamin_B2_mg": 0.0,
        "Vitamin_B3_mg": 0.0,
        "Vitamin_B6_mg": 0.0,
        "MUFA_g": 0.0,
        "PUFA_g": 0.0,
    }

    # CSV column index -> (output key, conversion factor)
    COLUMN_MAP = {
        0: ("name", None),  # handled separately as str
        1: ("Daily_Calories_kcal", 1.0),
        2: ("Protein_g", 1.0),
        3: ("Total_Fat_g", 1.0),
        4: ("Carbohydrates_g", 1.0),
        5: ("Sodium_mg", 1.0),
        6: ("Magnesium_mg", 1.0),
        7: ("Calcium_mg", 1.0),
        8: ("Iron_mg", 1.0),
        9: ("Zinc_mg", 1.0),
        10: ("Vitamin_A_mcg", 1.0),
        11: ("Vitamin_C_mg", 1.0),
        12: ("Vitamin_D_IU", 40.0),  # mcg -> IU
        13: ("Vitamin_E_mg", 1.0),
        14: ("Vitamin_K_mcg", 1.0),
        15: ("Vitamin_B1_mg", 1.0),
        16: ("Vitamin_B2_mg", 1.0),
        17: ("Vitamin_B3_mg", 1.0),
        18: ("Vitamin_B6_mg", 1.0),
        19: ("Vitamin_B12_mcg", 1.0),
        20: ("Saturated_Fat_g", 1.0),  # SFA
        21: ("MUFA_g", 1.0),
        22: ("PUFA_g", 1.0),
    }

    def parse_food_row(row: list) -> dict:
        """
        Parse a food CSV row (as a list of raw string values) into a
        standardised nutrient dict. Missing or unparseable values fall
        back to DEFAULTS.

        Parameters
        ----------
        row : list
            Ordered values matching the column layout:
            name, calories, proteins, fats, carbohydrates, sodium,
            Magnesium, calcium, iron, zinc, vitamin A, vitamin C,
            vitamin D, vitamin E, vitamin K, vitamin B1, vitamin B2,
            vitamin B3, vitamin B6, vitamin B12, SFA, MUFA, PUFA

        Returns
        -------
        dict
            Nutrient dict with float values and a 'name' str key.
            Keys not present in the input default to 0.0.
            Trans_Fat_g, Total_Sugar_g, Added_Sugar_g, Fiber_g, and
            Potassium_mg are not in the CSV format and default to 0.0.
        """
        result = dict(DEFAULTS)  # start with all defaults

        for idx, (key, factor) in COLUMN_MAP.items():
            # missing columns → keep default
            if idx >= len(row):
                continue

            raw = str(row[idx]).strip()

            if key == "name":
                result["name"] = raw
                continue

            if raw in ("", "-", "N/A", "None", "null"):
                continue  # keep default

            try:
                value = float(raw) * factor
            except ValueError:
                continue  # unparseable → keep default

            result[key] = value

        return result

def get_user_data():
    temp = input("use test data(y/n):\t")
    if temp == "n":
        fields = {
            "name": ("Name/ID", str),
            "height_cm": ("Height (cm)", float),
            "weight_kg": ("Weight (kg)", float),
            "Age": ("Age", int),
            "Gender": ("Gender (1=Male, 0=Female)", int),
            "Daily_Calories_kcal": ("Daily Calories (kcal)", float),
            "Carbohydrates_g": ("Carbohydrates (g)", float),
            "Protein_g": ("Protein (g)", float),
            "Total_Fat_g": ("Total Fat (g)", float),
            "Saturated_Fat_g": ("Saturated Fat (g)", float),
            "Trans_Fat_g": ("Trans Fat (g)", float),
            "Total_Sugar_g": ("Total Sugar (g)", float),
            "Added_Sugar_g": ("Added Sugar (g)", float),
            "Fiber_g": ("Fiber (g)", float),
            "Sodium_mg": ("Sodium (mg)", float),
            "Potassium_mg": ("Potassium (mg)", float),
            "Calcium_mg": ("Calcium (mg)", float),
            "Iron_mg": ("Iron (mg)", float),
            "Vitamin_D_IU": ("Vitamin D (IU)", float),
            "Vitamin_B12_mcg": ("Vitamin B12 (mcg)", float),
            "Physical_Activity_min": ("Physical Activity (min)", float),
            "Water_Intake_L": ("Water Intake (L)", float),
        }

        data = {}
        for key, (label, cast) in fields.items():
            while True:
                try:
                    raw = input(f"{label}:\t")
                    data[key] = cast(raw)
                    break
                except ValueError:
                    print(f"  Invalid input — please enter a valid {cast.__name__}.")
        return data

    else:
        return {
            "name": "P02 — Middle-aged obese male",
            "height_cm": 170, "weight_kg": 108, "Age": 48, "Gender": 1,
            "Daily_Calories_kcal": 3600, "Carbohydrates_g": 390, "Protein_g": 85,
            "Total_Fat_g": 160, "Saturated_Fat_g": 58, "Trans_Fat_g": 4.2,
            "Total_Sugar_g": 115, "Added_Sugar_g": 70, "Fiber_g": 7,
            "Sodium_mg": 4600, "Potassium_mg": 1100, "Calcium_mg": 480,
            "Iron_mg": 7, "Vitamin_D_IU": 90, "Vitamin_B12_mcg": 1.1,
            "Physical_Activity_min": 5, "Water_Intake_L": 0.9,
        }


def CLI_main():
    image = r"image1.jpg"

    model_paths = [
        r"srilankan_food_model_v21_74.5.pt",
        r"srilankan_food_model_v24_71.9.pt"
    ]

    model1_c = model1.EnsembleFoodDetector(model_paths)

    user_data = get_user_data()

    o1 = model1_c.quick_detect(image)

    print(f"\n\n\n=======================\n"
          f"operation 1: {o1}"
          f"\n=======================\n\n\n")

    if o1 != []:
        o2 = []
        for i in o1:
            print(f"\n----  now checking {i}")
            o2i = Est_Handler.main(i, "image")
            o2.append(o2i)

        print(f"\n\n\n=======================\n"
              f"operation 2: {o2}"
              f"\n=======================\n\n\n")

        o3 = []
        for i in o2:
            o3temp = a.compute_health_indexes(mo2_Parse(i))
            o3.append(o3temp)
        print(f"\n\n\n=======================\n"
                f"operation 3: {o3}"
                f"\n=======================\n\n\n")

        # Sanuli R's Module starts here
        #INPUTS
        # user data is variable "user_data"
        mo4_Parsed = [] # 2d list of all food items and dict of values needed
        for i in o2:
            o4_temp = mo4_Parse(i)
            mo4_Parsed.append(o4_temp)

    else:
        print("ERROR: no food items found")

if __name__ == "__main__":
    CLI_main()
