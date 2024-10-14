import csv
import json
import re

# Input CSV file path and output JSON file path
csv_file_path = '../output_Files/output.csv'
json_file_path = '../output_Files/output.json'

def convert_csv_to_single_json(csv_content):
    data = {}
    reader = csv.reader(csv_content.splitlines())
    for row in reader:
        if row and row[0].startswith('Table:'):
            # Skip the table header row
            continue
        if row and row[0]:  # Only process non-empty rows
            key = row[0]
            values = row[1:]  # Take all columns after the key
            data[key] = {
                "Value": values  # Store the values in a list or other desired format
            }
            with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=4)
        print(f"Data has been successfully converted to {json_file_path}")

    return data


