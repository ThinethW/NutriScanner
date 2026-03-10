import model1
from data_extraction_estimation import Est_Handler,Est_Handler,Label_Extraction

def CLI_main():
    model_paths = [
        r"srilankan_food_model_v21_74.5.pt",
        r"srilankan_food_model_v24_71.9.pt"
    ]

    model1_c = model1.EnsembleFoodDetector(model_paths)

    image = r"image2.jpg"

    o1 = model1_c.quick_detect(image)

    print(f"\n\n\n=======================\n"
          f"operation 1: {o1}"
          f"\n=======================\n\n\n")

    o2 = []
    for i in o1:
        print(f"\n----  now checking {i}")
        o2i = Est_Handler.Est_Handler(i,"image")
        o2.append(o2i)

    print(f"\n\n\n=======================\n"
          f"operation 2: {o2}"
          f"\n=======================\n\n\n")

if __name__ == "__main__":
    CLI_main()