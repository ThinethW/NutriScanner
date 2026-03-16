import time
import Est_Handler

if __name__ == "__main__":

    file_path = "international_fooditems.txt"

    # Load items from text file
    with open(file_path, "r", encoding="utf-8") as f:
        o1 = [line.strip() for line in f if line.strip()]

    o2 = []

    total_time = 0
    found = 0
    not_found = 0

    for i in o1:
        start = time.time()

        result = Est_Handler.Est_Handler(i, "image")

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