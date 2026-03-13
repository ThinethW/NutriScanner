import model1
from data_extraction_estimation import Est_Handler, Est_Handler, Label_Extraction
import nutritional_analysis.analyzer_refac as a


def mo2Parse():
    # test
    return {
        "Energy (kcal)": 450.0,
        "Total meal weight (g)": 350.0,
        "Carbohydrates digestible (g)": 52.3,
        "Total fiber (g)": 6.8,
        "Protein (g)": 28.5,
        "Sodium": 620.0,
        "SFA": 5.2,
        "MUFA": 8.7,
        "PUFA": 3.1,
    }


def CLI_main():
    image = r"image1.jpg"

    model_paths = [
        r"srilankan_food_model_v21_74.5.pt",
        r"srilankan_food_model_v24_71.9.pt"
    ]

    model1_c = model1.EnsembleFoodDetector(model_paths)


    o1 = model1_c.quick_detect(image)

    print(f"\n\n\n=======================\n"
          f"operation 1: {o1}"
          f"\n=======================\n\n\n")

    o2 = []
    for i in o1:
        print(f"\n----  now checking {i}")
        o2i = Est_Handler.Est_Handler(i, "image")
        o2.append(o2i)

    print(f"\n\n\n=======================\n"
          f"operation 2: {o2}"
          f"\n=======================\n\n\n")

    o3 = a.compute_health_indexes(mo2Parse())

    print(f"\n\n\n=======================\n"
          f"operation 3: {o3}"
          f"\n=======================\n\n\n")

if __name__ == "__main__":
    CLI_main()
