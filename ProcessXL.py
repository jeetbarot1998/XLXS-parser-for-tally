import pandas as pd
from enums.VoucherEnums import FinalVoucherColumns, SalesRate, PurchaseRate, MarkerInterface
from enums.purchase_sale_enums import string_enum_mapping
from utils import create_header_index_dict, get_row_as_dict, filter_dict
from validateXLSX import validate_excel_headers
from typing import Literal, Type, Dict, List, Union


class ProcessXL:

    def __init__(self, voucher_type: Literal["purchase", "sales"], xlsx_path: str):
        self.voucher_type = voucher_type  # purchase or sales only
        self.voucher_type_enum: MarkerInterface = self.get_voucher_enum(voucher_type)
        self.df = self.load_xlsx_to_df(xlsx_path)
        self.header_index_dict = create_header_index_dict(self.df)
        self.validate_xlsx()
        # Remove parenthesis and make it mm-dd-yyyy
        # self.df['Voucher Date'] = self.df['Voucher Date'].apply(self.convert_date)

        # Calculate total number of rows needed for pre-allocation
        total_rows = self.calculate_total_rows()
        # Pre-allocate the final DataFrame with NaN values
        self.final_voucher_df = pd.DataFrame(
            index=range(total_rows),
            columns=FinalVoucherColumns.get_all_string_values()
        )
        self.current_row_index = 0

    def calculate_total_rows(self) -> int:
        """
        Calculate the total number of rows needed in the final DataFrame
        """
        total_rows = 0
        for _, row in self.df.iterrows():
            # Add 1 for the first row
            total_rows += 1
            row_dict = get_row_as_dict(row, self.header_index_dict)

            # Add rows for each voucher category
            for category in self.voucher_type_enum.get_all_string_values():
                if row_dict.get(category) not in [0, 0.0, 0.00, "0"]:
                    # Add number of rows for this category
                    total_rows += len(string_enum_mapping.get(category).get_all_string_values())

            # Add 1 for rounded off entry
            total_rows += 1

        return total_rows

    def append_to_result_pandas(self, rows: Union[Dict, List[Dict]]) -> None:
        if isinstance(rows, dict):
            new_data = [rows]
        elif isinstance(rows, list):
            new_data = rows
        else:
            raise ValueError("Input must be a dictionary or a list of dictionaries")

        # Add the new data to pre-allocated DataFrame
        for row in new_data:
            for column, value in row.items():
                self.final_voucher_df.loc[self.current_row_index, column] = value
            self.current_row_index += 1

    # All other methods remain exactly the same
    def get_voucher_enum(self, voucher_type_str) -> Type[PurchaseRate] | Type[SalesRate] | None:
        voucher_type = {
            "sales": SalesRate,
            "purchase": PurchaseRate
        }
        return voucher_type.get(voucher_type_str)

    def load_xlsx_to_df(self, path):
        return pd.read_excel(path)

    def validate_xlsx(self):
        return validate_excel_headers(self.header_index_dict, self.voucher_type_enum)

    def rounding_column(self, column_name: str, rounded_by: int):
        numeric_column = pd.to_numeric(self.df[column_name], errors='coerce')
        rounded_column = numeric_column.round(rounded_by)
        self.df[column_name] = rounded_column

    def convert_columns_to_numeric(self):
        for each_col in self.voucher_type_enum.get_all_string_values():
            if each_col in self.header_index_dict.keys():
                self.rounding_column(each_col, 2)

    def convert_date(self, date_str):
        date_str = date_str.strip("'")
        date = pd.to_datetime(date_str, format='%d-%m-%Y')
        return date.strftime('%m-%d-%Y')

    def process_rows(self):
        self.convert_columns_to_numeric()
        for index, row in self.df.iterrows():
            print(f"\nProcessing row {index + 1}:")
            row = get_row_as_dict(row, self.header_index_dict)

            first_row = self.append_first_row(row)

            row_sum = 0
            for each_voucher_category in self.voucher_type_enum.get_all_string_values():
                if row.get(each_voucher_category) not in [0, 0.0, 0.00, "0"]:
                    rows_to_insert, each_voucher_sum = self.make_entry_for_category(row, each_voucher_category)
                    self.append_to_result_pandas(rows_to_insert)
                    row_sum += each_voucher_sum
                else:
                    continue

            rounded_off_by = first_row.get(FinalVoucherColumns.LEDGER_AMOUNT.value) - row_sum
            self.append_rounded_off(rounded_off_by)

        # Remove any unused pre-allocated rows
        self.final_voucher_df = self.final_voucher_df.iloc[:self.current_row_index]
        self.final_voucher_df.to_excel('output.xlsx', index=False)

    def append_rounded_off(self, difference):
        rounded_off_dic = dict()
        rounded_off_dic[FinalVoucherColumns.LEDGER_NAME.value] = FinalVoucherColumns.ROUNDED_OFF.value
        rounded_off_dic[FinalVoucherColumns.LEDGER_AMOUNT.value] = difference
        rounded_off_dic[FinalVoucherColumns.LEDGER_AMOUNT_DR_CR.value] = self.get_type_cr_dr()
        self.append_to_result_pandas(rounded_off_dic)

    def get_type_cr_dr(self):
        return "DR" if self.voucher_type == "purchase" else "CR"

    def append_first_row(self, row):
        first_row = self.populate_first_entry(row)
        first_row[FinalVoucherColumns.LEDGER_AMOUNT.value] = row.get(FinalVoucherColumns.LEDGER_AMOUNT.value)
        self.append_to_result_pandas(first_row)
        return first_row

    def make_entry_for_category(self, row, voucher_category):
        keys_to_populate = string_enum_mapping.get(voucher_category).get_all_string_values()
        list_of_dict = []
        sum = 0

        for keys in keys_to_populate:
            dic = {}
            dic[FinalVoucherColumns.LEDGER_NAME.value] = keys
            ledger_amount = row.get(keys)
            dic[FinalVoucherColumns.LEDGER_AMOUNT.value] = ledger_amount
            sum += ledger_amount
            dic[FinalVoucherColumns.LEDGER_AMOUNT_DR_CR.value] = self.get_type_cr_dr()
            list_of_dict.append(dic)
        return list_of_dict, sum

    def populate_first_entry(self, row):
        first_row_for_entry = filter_dict(row, FinalVoucherColumns.get_all_string_values())
        first_row_for_entry[FinalVoucherColumns.LEDGER_NAME.value] = row.get(FinalVoucherColumns.LEDGER_NAME.value)
        first_row_for_entry[
            FinalVoucherColumns.LEDGER_AMOUNT_DR_CR.value] = "DR" if self.voucher_type == "sales" else "CR"
        return first_row_for_entry


ProcessXL("sales", "processed_gst_data final.xlsx").process_rows()