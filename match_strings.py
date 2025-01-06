import csv
import difflib
import re


def calculate_similarity(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).ratio()


def remove_duplicates(input_list):
    seen = set()
    return [x for x in input_list if not (x in seen or seen.add(x))]


def find_closest_matches(file_a, file_b, lambda_a, lambda_b, threshold=0.5):
    with open(file_a, 'r') as f:
        lines_a = remove_duplicates([lambda_a(line.strip()).strip() for line in f.readlines()])

    with open(file_b, 'r') as f:
        lines_b = remove_duplicates([lambda_b(line.strip()).strip() for line in f.readlines()])

    matches = []
    unmatched_lines_a = []

    for string_a in lines_a:
        best_match = None
        highest_similarity = 0

        # Find the closest match in file B that is above the threshold
        for string_b in lines_b:
            similarity = calculate_similarity(string_a, string_b)
            if similarity > highest_similarity and similarity >= threshold:
                highest_similarity = similarity
                best_match = string_b

        if best_match:
            matches.append((string_a, best_match, highest_similarity))
            # Remove the matched line from file B to avoid re-matching
            lines_b.remove(best_match)
        else:
            unmatched_lines_a.append((string_a, '', 0))

    matches.extend(unmatched_lines_a)
    for string_b in lines_b:
        matches.append(('', string_b, 0))

    return matches


def write_to_csv(matches, output_file):
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['a', 'b', '%'])
        for a, b, similarity in matches:
            writer.writerow([a, b, round(similarity * 100, 2)])


def remove_string_from_list(s: str, list_to_remove: list[str]) -> str:
    for r in list_to_remove:
        s = s.replace(r, '')
    return s


def remove_with_regex(s: str, pattern: str) -> str:
    s = re.sub(pattern, '', s)
    return s


def treat_a(string_a: str) -> str:
    string_a = remove_with_regex(string_a, r'\([^()]*\)')
    return string_a


def treat_b(string_b: str) -> str:
    string_b = string_b.removesuffix('.zip')
    string_b = remove_with_regex(string_b, r'\([^()]*\)')
    return string_b


def match_and_report(file_a: str, file_b: str, output_csv: str):
    matches = find_closest_matches(file_a, file_b, treat_a, treat_b)
    write_to_csv(matches, output_csv)
    print(f"Matches written to {output_csv}")


def main():
    file_a = 'dontcommit/a.txt'
    file_b = 'dontcommit/b.txt'
    output_csv = 'matches.csv'
    match_and_report(file_a, file_b, output_csv)


if __name__ == '__main__':
    main()
