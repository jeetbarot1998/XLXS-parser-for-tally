import pandas as pd

from enums.VoucherEnums import FinalVoucherColumns, SalesRate, PurchaseRate, MarkerInterface
from utils import create_header_index_dict, get_field_data_by_header_name, get_row_as_dict, filter_dict
from validateXLSX import validate_excel_headers


class ProcessXL:

    def __init__(self, voucher_type: str, xlsx_path: str):
        self.voucher_type: str = voucher_type # purchase or sales only
        self.voucher_type_enum: MarkerInterface = self.get_voucher_enum(voucher_type)
        self.df = self.load_xlsx_to_df(xlsx_path)
        self.final_voucher_df = pd.DataFrame(columns=FinalVoucherColumns.get_all_string_values())
        self.header_index_dict = create_header_index_dict(self.df)

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

    def process_rows(self):
        end_counter_new_df = len(self.final_voucher_df)
        self.convert_columns_to_numeric()
        for index, row in self.df.iterrows():
            print(f"\nProcessing row {index + 1}:")


            # voucher_date = get_field_data_by_header_name(row_data=row,
            #                                            headers=header_index_dict,
            #                                            search_text=FinalVoucherColumns.VOUCHER_DATE.value)

            row = get_row_as_dict(row, self.header_index_dict)

            # Populate first row for an entry
            self.populate_first_entry(row, end_counter_new_df)
            end_counter_new_df += 1

            # TODO:
            #  1.Check for each type of tax, and make 3 rows for each tax type
            #  2. Make a function and pass each tax type and return 3 rows for each type
            #  3. At the end of checking for each tax type, concat all the rows to the new df
            #  4. If possible integrate it with populate first row method.


            print(self.final_voucher_df)

    def populate_first_entry(self, row, end_counter_new_df):
        first_row_for_entry = filter_dict(row, FinalVoucherColumns.get_all_string_values())
        self.final_voucher_df.loc[end_counter_new_df] = first_row_for_entry


ProcessXL("purchase", "../test.xlsx").process_rows()
