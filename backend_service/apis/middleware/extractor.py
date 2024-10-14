import boto3
import sys
import os
# from pprint import pprint
from dotenv import load_dotenv

def initialize_textract_client():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.join(current_dir, '.', '.env')
    load_dotenv(dotenv_path)

    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION")
    
    if not all([aws_access_key, aws_secret_key, aws_region]):
        print("AWS credentials not found in environment variables.")
        return None

    # Initialize boto3 client with explicit credentials from environment
    client = boto3.client(
        'textract',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )
    return client

def generate_csv_from_blocks(blocks):
    blocks_map = {block['Id']: block for block in blocks}
    table_blocks = [block for block in blocks if block['BlockType'] == 'TABLE']
    if not table_blocks:
        return "NO Table FOUND"

    csv_data = ""
    for index, table in enumerate(table_blocks):
        rows, _ = get_rows_columns_map(table, blocks_map)
        csv_data += format_rows_as_csv(rows, index + 1)

    return csv_data

def get_rows_columns_map(table_result, blocks_map):
    """Map rows and columns of the table along with confidence scores."""
    rows = {}
    for relationship in table_result.get('Relationships', []):
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                cell = blocks_map[child_id]
                if cell['BlockType'] == 'CELL':
                    row_index = cell['RowIndex']
                    col_index = cell['ColumnIndex']
                    if row_index not in rows:
                        rows[row_index] = {}
                    rows[row_index][col_index] = get_cell_text(cell, blocks_map)
    return rows, []



def get_cell_text(cell, blocks_map):
    text = ' '.join(
        word['Text'] for relationship in cell.get('Relationships', [])
        for child_id in relationship['Ids']
        if (word := blocks_map.get(child_id)) and word['BlockType'] == 'WORD'
    )
    return text.strip()


def extract_tables_from_images(file_name):
    """Process the image using Textract to extract tables and generate CSV."""
    client= initialize_textract_client()

    try:
        with open(file_name,'rb') as file:
            img_test = file.read()
        print('Image loaded:', file_name)
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)
    
    try:
        response = client.analyze_document(Document={'Bytes': img_test}, FeatureTypes=['TABLES'])
    except Exception as e:
        print(f"Error calling Textract: {e}")
        sys.exit(1)

    # Get the blocks from the response
    blocks = response.get('Blocks', [])
    # blocks_map = {block['Id']: block for block in blocks} 

    return blocks



def format_rows_as_csv(rows, table_index):
    csv_lines = [f'Table: Table_{table_index}\n']
    for row_index in sorted(rows):
        csv_lines.append(','.join(rows[row_index].values()) + '\n')
    return ''.join(csv_lines)




def extract_main(file_name):
    """Main function to generate and save CSV output."""
    
    blocks = extract_tables_from_images(file_name)
    csv_data = generate_csv_from_blocks(blocks)
    output_file = '../output_Files/output.csv'
    print("OUTPUT FILE PATH: " + output_file)

    try:
        with open(output_file, "wt") as fout:
            fout.write(csv_data)
        print(f'CSV OUTPUT FILE:{output_file}')
    except Exception as e:
        print(f"Error writing CSV file: {e}")
        sys.exit(1)
    return csv_data

