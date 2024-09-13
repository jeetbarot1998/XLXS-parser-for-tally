import pandas as pd

from enums.VoucherEnums import FinalVoucherColumns, SalesRate, PurchaseRate, MarkerInterface
from enums.purchase_sale_enums import string_enum_mapping
from utils import create_header_index_dict, get_field_data_by_header_name, get_row_as_dict, filter_dict
from validateXLSX import validate_excel_headers
from typing import Literal


class ProcessXL:

    def __init__(self, voucher_type: Literal["purchase", "sales"], xlsx_path: str):
        self.voucher_type = voucher_type  # purchase or sales only
        self.voucher_type_enum: MarkerInterface = self.get_voucher_enum(voucher_type)
        self.df = self.load_xlsx_to_df(xlsx_path)
        self.header_index_dict = create_header_index_dict(self.df)
        self.validate_xlsx()
        # TODO : remove parenthesis and make it mm-dd-yyyy
        # self.df['Voucher Date'] = self.df['Voucher Date'].apply(self.convert_date)
        self.final_voucher_df = pd.DataFrame(columns=FinalVoucherColumns.get_all_string_values())

    def get_voucher_enum(self, voucher_type_str) -> MarkerInterface:
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
        """
        Convert the column in df to numerical rounded off
        :parameter column_name : str : name of column to convert
        :parameter rounded_by : int : how much to round by
        :return: void
        """
        numeric_column = pd.to_numeric(self.df[column_name], errors='coerce')
        # Round to 2 decimal points
        rounded_column = numeric_column.round(rounded_by)
        # Update the original DataFrame
        self.df[column_name] = rounded_column

    def convert_columns_to_numeric(self):
        """
        convert respective columns as per type of voucher to numerical values
        :return: void
        """
        for each_col in self.voucher_type_enum.get_all_string_values():
            if each_col in self.header_index_dict.keys():
                self.rounding_column(each_col, 2)

    def convert_date(self, date_str):
        # Remove any single quotes
        date_str = date_str.strip("'")
        date = pd.to_datetime(date_str, format='%d-%m-%Y')
        # Convert to mm-dd-yyyy format
        return date.strftime('%m-%d-%Y')

    def process_rows(self):
        self.convert_columns_to_numeric()
        for index, row in self.df.iterrows():
            print(f"\nProcessing row {index + 1}:")

            # voucher_date = get_field_data_by_header_name(row_data=row,
            #                                            headers=header_index_dict,
            #                                            search_text=FinalVoucherColumns.VOUCHER_DATE.value)

            row = get_row_as_dict(row, self.header_index_dict)

            for each_voucher_category in self.voucher_type_enum.get_all_string_values():
                if row.get(each_voucher_category) not in [0, 0.0, 0.00, "0"]:
                    self.final_voucher_df = pd.concat([self.final_voucher_df, self.make_entry_for_category(row, each_voucher_category)], ignore_index=True)
                    # print(self.final_voucher_df)
                else:
                    continue

            # print(self.final_voucher_df)
        self.final_voucher_df.to_excel('output.xlsx', index=False)

    def make_entry_for_category(self, row, voucher_category):
        # getting all the keys for which we have to search in the row
        keys_to_populate = string_enum_mapping.get(voucher_category).get_all_string_values()
        list_of_dict = []
        # Append response of first row for this entry in the list
        list_of_dict.append(self.populate_first_entry(row))
        for keys in keys_to_populate:
            dic = {}
            dic[FinalVoucherColumns.LEDGER_NAME.value] = keys
            dic[FinalVoucherColumns.LEDGER_AMOUNT.value] = row.get(keys)
            dic[FinalVoucherColumns.LEDGER_AMOUNT_DR_CR.value] = "CR" if self.voucher_type == "purchase" else "DR"
            list_of_dict.append(dic)
        return pd.DataFrame(list_of_dict)

    def populate_first_entry(self, row):
        first_row_for_entry = filter_dict(row, FinalVoucherColumns.get_all_string_values())
        first_row_for_entry[FinalVoucherColumns.LEDGER_NAME.value] = "Cash Sales and Purchase"
        first_row_for_entry[FinalVoucherColumns.LEDGER_AMOUNT_DR_CR.value] = "CR" if self.voucher_type == "sales" else "DR"
        return first_row_for_entry

ProcessXL("purchase", "../test.xlsx").process_rows()
