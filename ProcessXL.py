import pandas as pd
from enums.VoucherEnums import FinalVoucherColumns, SalesRate, PurchaseRate, MarkerInterface
from enums.purchase_sale_enums import string_enum_mapping
from utils import create_header_index_dict, get_row_as_dict, filter_dict
from validateXLSX import validate_excel_headers
from typing import Literal, Type, Dict, List, Union


class ProcessXL:

    def __init__(self, voucher_type: Literal["purchase", "sales"], xlsx_path: str):
        self.voucher_type = voucher_type  # purchase or sales only`
        self.voucher_type_enum: MarkerInterface = self.get_voucher_enum(voucher_type)
        self.df = self.load_xlsx_to_df(xlsx_path)
        self.header_index_dict = create_header_index_dict(self.df)
        self.validate_xlsx()
        # Remove parenthesis and make it mm-dd-yyyy
        self.df['Voucher Date'] = self.df['Voucher Date'].apply(self.convert_date)
        self.final_voucher_df = pd.DataFrame(columns=FinalVoucherColumns.get_all_string_values())

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
        """ Convert string "dd-mm-yyyy" or date dd-mm-yyyy to TYPE date in XLSX
        format dd/mm/yyyy """
        # Remove any single quotes
        date_str = date_str.strip("'")
        date = pd.to_datetime(date_str, format='%d-%m-%Y')
        # Convert to mm-dd-yyyy format
        return date.strftime('%m-%d-%Y')

    def process_rows(self):
        self.convert_columns_to_numeric()
        for index, row in self.df.iterrows():
            print(f"\nProcessing row {index + 1}:")
            row = get_row_as_dict(row, self.header_index_dict)

            # Populate first row.
            first_row = self.append_first_row(row)

            row_sum = 0
            for each_voucher_category in self.voucher_type_enum.get_all_string_values():
                # TODO: Handle exception if the key does not exist int the dict => Use default dict \
                #  in line 73.
                if row.get(each_voucher_category) not in [0, 0.0, 0.00, "0"]:
                    rows_to_insert, each_voucher_sum = self.make_entry_for_category(row, each_voucher_category)
                    self.append_to_result_pandas(rows_to_insert)
                    # Add to the sum
                    row_sum += each_voucher_sum
                else:
                    continue

            rounded_off_by = first_row.get(FinalVoucherColumns.LEDGER_AMOUNT.value) - row_sum
            self.append_rounded_off(rounded_off_by)
            # print(self.final_voucher_df)
        self.final_voucher_df.to_excel('output.xlsx', index=False)

    def append_rounded_off(self, difference):
        rounded_off_dic = dict()
        rounded_off_dic[FinalVoucherColumns.LEDGER_NAME.value] = FinalVoucherColumns.ROUNDED_OFF.value
        rounded_off_dic[FinalVoucherColumns.LEDGER_AMOUNT.value] = difference
        rounded_off_dic[FinalVoucherColumns.LEDGER_AMOUNT_DR_CR.value] = \
            self.get_type_cr_dr()
        self.append_to_result_pandas(rounded_off_dic)

    def get_type_cr_dr(self):
        return "DR" if self.voucher_type == "purchase" else "CR"

    def append_first_row(self, row):
        first_row = self.populate_first_entry(row)
        first_row[FinalVoucherColumns.LEDGER_AMOUNT.value] = row.get(FinalVoucherColumns.LEDGER_AMOUNT.value)
        self.append_to_result_pandas(first_row)
        return first_row

    def append_to_result_pandas(self, rows: Union[Dict, List[Dict]]) -> None:
        if isinstance(rows, dict):
            new_data = [rows]  # Convert single dictionary to a list
        elif isinstance(rows, list):
            new_data = rows  # Use the list as is
        else:
            raise ValueError("Input must be a dictionary or a list of dictionaries")

        self.final_voucher_df = pd.concat([self.final_voucher_df,
                                           pd.DataFrame(new_data)],
                                          ignore_index=True)

    def make_entry_for_category(self, row, voucher_category):
        # getting all the keys for which we have to search in the row
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
        first_row_for_entry[FinalVoucherColumns.LEDGER_AMOUNT_DR_CR.value] = "DR" if self.voucher_type == "sales" else "CR"
        return first_row_for_entry

ProcessXL("purchase", "../test.xlsx").process_rows()
