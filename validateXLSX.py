from enums.VoucherEnums import get_all_enum_values, MarkerInterface


def validate_excel_headers(header_index_dict:dict, exclude: MarkerInterface = None) -> bool:
    # Get the headers from the DataFrame
    headers = set(header_index_dict.keys())

    if exclude is None:
        expected_columns = set(get_all_enum_values())
    else:
        expected_columns = set(get_all_enum_values(exclude))

    # Check if all expected columns are present in the headers
    missing_columns = expected_columns - headers

    if not missing_columns:
        print("All expected columns are present in the Excel file.")
        return True
    else:
        print("Missing columns:", missing_columns)
        return False