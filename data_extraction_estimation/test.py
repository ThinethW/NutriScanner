if __name__ == "__main__":
    import Estimation_Search

    # Debug: peek at what the USDA file actually looks like
    import csv

    with open("USDA.csv", newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f))
    print("Header row:", rows[0])
    print("First data row:", rows[1])
    print("Second data row:", rows[2])
    print()

    # Also test the match_rate function directly
    test_input = "fried rice"
    test_db = rows[1][0]  # First actual food name in USDA
    print(f"Sample match_rate('{test_input}', '{test_db}') = {Estimation_Search.match_rate(test_input, test_db)}")
    print()