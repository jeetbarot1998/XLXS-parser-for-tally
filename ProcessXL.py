import pandas as pd
from enums.VoucherEnums import FinalVoucherColumns, SalesRate, PurchaseRate, MarkerInterface
from enums.purchase_sale_enums import string_enum_mapping
from utils import create_header_index_dict, get_row_as_dict, filter_dict
from validateXLSX import validate_excel_headers
from typing import Literal, Type, Dict, List, Union


class ProcessXL:
    def __init__(self, voucher_type: Literal["purchase", "sales"], xlsx_path: str):
        self.voucher_type = voucher_type
        self.voucher_type_enum: MarkerInterface = self._get_voucher_enum(voucher_type)

        # Load Excel file more efficiently
        self.df = pd.read_excel(
            xlsx_path,
            dtype={col: 'float64' for col in self.voucher_type_enum.get_all_string_values()},
            parse_dates=['Voucher Date']
        )

        self.header_index_dict = create_header_index_dict(self.df)
        self.validate_xlsx()

        # Pre-allocate final DataFrame with estimated size
        # ===================================================
        # NOTE: CHANGE THIS 5 to 5+ if values are not consistent
        # ===================================================
        estimated_rows = len(self.df) * 5  # Estimate based on typical number of entries per row
        self.final_voucher_df = pd.DataFrame(
            index=range(estimated_rows),
            columns=FinalVoucherColumns.get_all_string_values()
        )
        self.current_row_index = 0

    @staticmethod
    def _get_voucher_enum(voucher_type_str) -> Type[PurchaseRate] | Type[SalesRate] | None:
        return {"sales": SalesRate, "purchase": PurchaseRate}.get(voucher_type_str)

    def validate_xlsx(self):
        return validate_excel_headers(self.header_index_dict, self.voucher_type_enum)

    def convert_columns_to_numeric(self):
        """Convert columns to numeric using vectorized operations"""
        cols_to_convert = [
            col for col in self.voucher_type_enum.get_all_string_values()
            if col in self.header_index_dict
        ]
        self.df[cols_to_convert] = self.df[cols_to_convert].round(2)

    def _append_to_result_pandas(self, rows: Union[Dict, List[Dict]]) -> None:
        """More efficient append using pre-allocated DataFrame"""
        if isinstance(rows, dict):
            rows = [rows]

        num_rows = len(rows)
        end_idx = self.current_row_index + num_rows

        for i, row in enumerate(rows):
            for col, val in row.items():
                self.final_voucher_df.iloc[self.current_row_index + i,
                self.final_voucher_df.columns.get_loc(col)] = val

        self.current_row_index = end_idx

    def make_entry_for_category(self, row, voucher_category):
        keys_to_populate = string_enum_mapping.get(voucher_category).get_all_string_values()
        cr_dr_value = self.get_type_cr_dr()

        # Pre-allocate lists for better performance
        list_of_dict = []
        total_sum = 0

        for key in keys_to_populate:
            ledger_amount = row.get(key, 0)
            if ledger_amount:  # Only process non-zero amounts
                total_sum += ledger_amount
                list_of_dict.append({
                    FinalVoucherColumns.LEDGER_NAME.value: key,
                    FinalVoucherColumns.LEDGER_AMOUNT.value: ledger_amount,
                    FinalVoucherColumns.LEDGER_AMOUNT_DR_CR.value: cr_dr_value
                })

        return list_of_dict, total_sum

    def process_rows(self):
        self.convert_columns_to_numeric()

        # Process rows in chunks for better performance
        chunk_size = 1000
        for chunk_start in range(0, len(self.df), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(self.df))
            chunk = self.df.iloc[chunk_start:chunk_end]

            for idx, row in chunk.iterrows():
                print("processing row = " + str(idx))
                row_dict = get_row_as_dict(row, self.header_index_dict)

                # Process first row
                first_row = self.append_first_row(row_dict)
                row_sum = 0

                # Process categories
                for category in self.voucher_type_enum.get_all_string_values():
                    if row_dict.get(category, 0) not in [0, 0.0, 0.00, "0"]:
                        rows_to_insert, category_sum = self.make_entry_for_category(row_dict, category)
                        self._append_to_result_pandas(rows_to_insert)
                        row_sum += category_sum

                # Handle rounding
                rounded_off_by = first_row.get(FinalVoucherColumns.LEDGER_AMOUNT.value) - row_sum
                if abs(rounded_off_by) > 0.01:  # Only append if significant
                    self.append_rounded_off(rounded_off_by)

        # Trim unused rows and save
        self.final_voucher_df = self.final_voucher_df.iloc[:self.current_row_index].copy()
        self.final_voucher_df.to_excel('output.xlsx', index=False)

    def append_rounded_off(self, difference):
        if abs(difference) > 0.01:  # Only process significant differences
            self._append_to_result_pandas({
                FinalVoucherColumns.LEDGER_NAME.value: FinalVoucherColumns.ROUNDED_OFF.value,
                FinalVoucherColumns.LEDGER_AMOUNT.value: difference,
                FinalVoucherColumns.LEDGER_AMOUNT_DR_CR.value: self.get_type_cr_dr()
            })

    def get_type_cr_dr(self):
        return "DR" if self.voucher_type == "purchase" else "CR"

    def append_first_row(self, row):
        first_row = self.populate_first_entry(row)
        first_row[FinalVoucherColumns.LEDGER_AMOUNT.value] = row.get(FinalVoucherColumns.LEDGER_AMOUNT.value)
        self._append_to_result_pandas(first_row)
        return first_row

    def populate_first_entry(self, row):
        first_row = filter_dict(row, FinalVoucherColumns.get_all_string_values())
        first_row[FinalVoucherColumns.LEDGER_NAME.value] = row.get(FinalVoucherColumns.LEDGER_NAME.value)
        first_row[FinalVoucherColumns.LEDGER_AMOUNT_DR_CR.value] = "DR" if self.voucher_type == "sales" else "CR"
        return first_row


if __name__ == "__main__":
    ProcessXL("sales", "processed_gst_data final.xlsx").process_rows()