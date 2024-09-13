import re
from datetime import datetime


def create_header_index_dict(df):
    return {column: index for index, column in enumerate(df.columns)}


def get_field_data_by_header_name(row_data, headers: dict, search_text:str):
    return row_data.iloc[headers[search_text]]


def get_row_as_dict(row, header_index_dict) -> dict:
    return {column: row.iloc[col_index] for column, col_index in header_index_dict.items()}


def parse_date(date_string):
    try:
        # Parse the date string assuming DD-MM-YYYY format
        return datetime.strptime(date_string, '%d-%m-%Y')
    except ValueError:
        print(f"Error parsing date: {date_string}. Make sure it's in DD-MM-YYYY format.")
        return None


def is_valid_date_format(date_string):
    """Check if the date string is in dd-mm-yyyy format."""
    pattern = r'^\d{2}-\d{2}-\d{4}$'
    return bool(re.match(pattern, date_string))


def convert_date_format(date_string):
    """Convert date from dd-mm-yyyy to mm-dd-yyyy format."""
    if not is_valid_date_format(date_string):
        print(f"Error: Invalid date format: {date_string}. Expected dd-mm-yyyy.")
        return None

    day, month, year = date_string.split('-')
    return f"{month}-{day}-{year}"


def filter_dict(original_dict, keys_to_keep):
    return {key: original_dict[key] for key in keys_to_keep if key in original_dict}