import csv
import os
import re
from difflib import SequenceMatcher


def normalize_name(name: str) -> set:
    """
    Normalize a food name into a set of words for comparison.
    Removes punctuation, spaces, capitalization differences.
    Splits into individual words so order doesn't matter.
    e.g. "Rice, Fried" and "fried rice" both become {"rice", "fried"}
    """
    name = name.lower()
    name = re.sub(r'[^a-z0-9\s]', '', name)  # Remove punctuation
    return set(name.split())                   # Split into word set


def match_rate(input_name: str, db_name: str) -> float:
    """
    Compare two food names by:
    1. Word overlap (order/punctuation/case insensitive)
    2. Fuzzy character similarity as a tiebreaker
    Returns a match score between 0.0 and 1.0
    """
    input_words = normalize_name(input_name)
    db_words = normalize_name(db_name)

    if not input_words or not db_words:
        return 0.0

    # Word overlap score (Jaccard similarity)
    intersection = input_words & db_words
    union = input_words | db_words
    word_score = len(intersection) / len(union)

    # Fuzzy character similarity as tiebreaker
    fuzzy_score = SequenceMatcher(
        None,
        ' '.join(sorted(input_words)),
        ' '.join(sorted(db_words))
    ).ratio()

    # Weight word overlap more heavily
    return (word_score * 0.7) + (fuzzy_score * 0.3)


def get_item_values(item_name: str) -> tuple:
    """
    Search for a food item across databases using fuzzy matching.
    - Stores candidates with match rate > 60%
    - Returns immediately if match rate > 80%
    - Returns best candidate above 60% if no 80%+ match found
    - Returns empty tuple if nothing above 60%
    """
    best_candidate = ()
    best_score = 0.0

    csv_files = [
        ("FrequentedData.csv", True,  True),
        ("IRD.csv",            False, False),
        ("External.csv",       False, False),
        ("Fastfood.csv",       False, False),
        ("USDA.csv",           False, True),
    ]

    for filename, reverse, yoda in csv_files:
        if not yoda:
            continue
        if not os.path.exists(filename):
            continue

        with open(filename, newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))

        # Skip header row if present
        data_rows = rows[1:] if rows and rows[0][0].lower() == 'description' else rows
        search_order = reversed(data_rows) if reverse else iter(data_rows)

        for row in search_order:
            if not row:
                continue

            score = match_rate(item_name, row[0])

            # Immediate return if high confidence
            if score >= 0.80:
                values = tuple(row)
                _append_to_frequented(values)
                return values

            # Store as candidate if above threshold
            if score > best_score and score >= 0.60:
                best_score = score
                best_candidate = tuple(row)

    # Return best candidate found above 60%
    if best_candidate:
        _append_to_frequented(best_candidate)

    return best_candidate


def _append_to_frequented(values: tuple) -> None:
    """Append a found item to FrequentedData.csv."""
    freq_path = "FrequentedData.csv"
    file_exists = os.path.exists(freq_path)

    with open(freq_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        if not file_exists or os.path.getsize(freq_path) == 0:
            writer.writerow([
                "description", "calories", "proteins", "fats", "carbohydrates",
                "sodium", "Magnesium", "calcium", "iron", "zinc",
                "vitamin A", "vitamin C", "vitamin D", "vitamin E", "vitamin K",
                "vitamin B1", "vitamin B2", "vitamin B3", "vitamin B6", "vitamin B12"
            ])

        writer.writerow(list(values))


# Test
if __name__ == "__main__":
    item = input("Enter item name: ")
    result = get_item_values(item)

    if result:
        headers = [
            "description", "calories", "proteins", "fats", "carbohydrates",
            "sodium", "Magnesium", "calcium", "iron", "zinc",
            "vitamin A", "vitamin C", "vitamin D", "vitamin E", "vitamin K",
            "vitamin B1", "vitamin B2", "vitamin B3", "vitamin B6", "vitamin B12"
        ]
        print("\nNutritional Values:")
        for header, value in zip(headers, result):
            print(f"  {header}: {value}")
    else:
        print(f"Item '{item}' not found in any database.")