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


def hail_mary(item_name: str, csv_files: list) -> tuple:
    """
    Last resort search - looks for entries that contain all input words
    in any order, then returns the one with the fewest total words.
    Respects yoda flag - only searches enabled files.
    e.g. "fried rice" will match "Restaurant, Chinese, fried rice, without meat, vegan"
    and "Restaurant, Chinese, fried rice, with meat, non vegan"
    but returns the one with fewer words.
    """
    input_words = normalize_name(item_name)
    candidates = []

    for filename, reverse, yoda in csv_files:
        if not yoda:
            print("hail mary skipping (not yoda):", filename)
            continue
        if not os.path.exists(filename):
            print("hail mary skipping (not found):", filename)
            continue

        with open(filename, newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))

        data_rows = rows[1:] if rows and rows[0][0].lower() == 'description' else rows

        for row in data_rows:
            if not row:
                continue

            db_words = normalize_name(row[0])

            # All input words must be present in the db entry
            if input_words.issubset(db_words):
                candidates.append((len(db_words), row))

    if not candidates:
        return ()

    # Return the entry with the fewest words (least extra context)
    candidates.sort(key=lambda x: x[0])
    return tuple(candidates[0][1])


def get_item_values(item_name: str) -> tuple:
    """
    Search for a food item across databases using fuzzy matching.
    - Stores candidates with match rate > 20%
    - Returns immediately if match rate > 80%
    - Returns best candidate above 20% if no 80%+ match found
    - Hail mary search if nothing found above 20%
    - Returns empty tuple if nothing found at all
    """
    best_candidate = ()
    best_score = 0.0

    csv_files = [
        ("data_extraction_estimation/FrequentedData.csv",              True,  True),
        ("data_extraction_estimation/module_2_datasets/IRD.csv",       False, True),
        ("data_extraction_estimation/module_2_datasets/External.csv",  False, False),
        ("data_extraction_estimation/module_2_datasets/Fastfood.csv",  False, False),
        ("data_extraction_estimation/module_2_datasets/USDA.csv",      False, True),
    ]

    for filename, reverse, yoda in csv_files:
        if not yoda:
            print("not yoda:", filename)
            continue
        if not os.path.exists(filename):
            print("not found:", filename)
            continue

        with open(filename, newline='', encoding='utf-8') as f:
            print("reading", filename)
            rows = list(csv.reader(f))

        # Skip header row if present
        data_rows = rows[1:] if rows and rows[0][0].lower() == 'description' else rows
        search_order = reversed(data_rows) if reverse else iter(data_rows)

        for row in search_order:
            if not row:
                continue

            score = match_rate(item_name, row[0])

            # Immediate return if high confidence
            # quick return threshold here
            if score >= 0.80:
                values = tuple(row)
                _append_to_frequented(values)
                return values

            # Store as candidate if above threshold
            # Append Score threshold here
            if score > best_score and score >= 0.5:
                best_score = score
                best_candidate = tuple(row)

    # Return best candidate found above 20%
    if best_candidate:
        _append_to_frequented(best_candidate)
        return best_candidate

    # Hail mary - last resort, still respects yoda
    print("hail mary activated for:", item_name)
    hail_mary_result = hail_mary(item_name, csv_files)

    if hail_mary_result:
        _append_to_frequented(hail_mary_result)
        return hail_mary_result

    return ()


def _append_to_frequented(values: tuple) -> None:
    """Append a found item to FrequentedData.csv, then remove duplicates keeping the last occurrence."""
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

    # Read back, deduplicate keeping last occurrence
    with open(freq_path, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f))

    if not rows:
        return

    header = rows[0]
    data_rows = rows[1:]

    # Build dict keyed by description (row[0]), later rows overwrite earlier ones
    seen = {}
    for row in data_rows:
        if row:
            seen[row[0].strip().lower()] = row  # Last occurrence wins

    # Write back: header + deduplicated rows
    with open(freq_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(seen.values())


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