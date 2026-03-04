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
    return set(name.split())  # Split into word set


def match_rate(input_name: str, db_name: str) -> float:
    """
    Compare two food names using a plus/minus word scoring system.

    Plus points:  words in input that ARE in the db entry
    Minus points: words in db entry that are NOT in the input
                  (penalizes extra descriptors like "chinese, restaurant")

    Returns a match score between 0.0 and 1.0
    """
    input_words = normalize_name(input_name)
    db_words = normalize_name(db_name)

    if not input_words or not db_words:
        return 0.0

    # Words that match (plus points)
    matched = input_words & db_words

    # Words in db that aren't in input (minus points)
    extra_in_db = db_words - input_words

    # Words in input that aren't in db (minus points)
    missing_from_db = input_words - db_words

    # Scoring:
    # +1 for each matched word
    # -0.5 for each extra word in db not in input
    # -0.5 for each input word not found in db
    plus_points = len(matched)
    minus_points = (len(extra_in_db) * 0.5) + (len(missing_from_db) * 0.5)

    raw_score = plus_points - minus_points

    # Normalize against the larger of the two word sets
    # so score stays between 0 and 1
    max_possible = max(len(input_words), len(db_words))
    word_score = max(0.0, raw_score / max_possible)

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
    - Stores candidates with match rate > 20%
    - Returns immediately if match rate > 80%
    - Returns best candidate above 20% if no 80%+ match found
    - Returns empty tuple if nothing above 20%

    Plus/minus scoring means:
    - "fried rice" vs "fried rice, chinese, restaurant" still scores well
      since "fried" and "rice" match, extra words only slightly penalize
    """
    best_candidate = ()
    best_score = 0.0

    csv_files = [
        ("FrequentedData.csv", True, True),
        ("IRD.csv", False, False),
        ("External.csv", False, False),
        ("Fastfood.csv", False, False),
        ("USDA.csv", False, True),
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
            if score > best_score and score >= 0.20:
                best_score = score
                best_candidate = tuple(row)

    # Return best candidate found above 20%
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
