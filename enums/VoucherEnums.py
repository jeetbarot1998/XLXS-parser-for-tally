from enum import Enum

class MarkerInterface(Enum):
    ...

    @classmethod
    def get_all_string_values(cls):
        return [member.value for member in cls]

class FinalVoucherColumns(MarkerInterface):
    """ Final Voucher Columns"""
    VOUCHER_DATE = "Voucher Date"
    VOUCHER_TYPE_NAME = "Voucher Type Name"
    VOUCHER_NUMBER = "Voucher Number"
    LEDGER_NAME = "Ledger Name"
    LEDGER_AMOUNT = "Ledger Amount"
    LEDGER_AMOUNT_DR_CR = "Ledger Amount Dr/Cr"
    QUANTITY = "Quantity"
    ROUNDED_OFF = "Rounded off"


class InputVoucherColumns(MarkerInterface):
    VOUCHER_DATE = FinalVoucherColumns.VOUCHER_DATE.value
    VOUCHER_TYPE_NAME = FinalVoucherColumns.VOUCHER_TYPE_NAME.value
    VOUCHER_NUMBER = FinalVoucherColumns.VOUCHER_NUMBER.value
    LEDGER_NAME = FinalVoucherColumns.LEDGER_NAME.value
    LEDGER_AMOUNT = FinalVoucherColumns.LEDGER_AMOUNT.value
    LEDGER_AMOUNT_DR_CR = FinalVoucherColumns.LEDGER_AMOUNT_DR_CR.value
    QUANTITY = FinalVoucherColumns.QUANTITY.value


class SalesRate(MarkerInterface):
    SALES_28_PERCENT = "Sales@28%"
    SALES_18_PERCENT = "Sales@18%"
    SALES_12_PERCENT = "Sales@12%"
    SALES_5_PERCENT = "Sales@5%"


class PurchaseRate(MarkerInterface):
    PURCHASE_28_PERCENT = "Purchase@28%"
    PURCHASE_18_PERCENT = "Purchase@18%"
    PURCHASE_12_PERCENT = "Purchase@12%"
    PURCHASE_5_PERCENT = "Purchase@5%"


class TaxRate(MarkerInterface):
    CGST_28_PERCENT = "14%CGST"
    SGST_28_PERCENT = "14%SGST"
    CGST_18_PERCENT = "9%CGST"
    SGST_18_PERCENT = "9%SGST"
    CGST_12_PERCENT = "6%CGST"
    SGST_12_PERCENT = "6%SGST"
    CGST_5_PERCENT = "2.5%CGST"
    SGST_5_PERCENT = "2.5%SGST"


class Miscellaneous(MarkerInterface):
    TAX_FREE = "TAXFREE"
    CESS_RS = "CessRs"
    ROUND_OFF = "RNDOFF"


def parse_string(value: str, classToParse: MarkerInterface) -> bool:
    try:
        response = classToParse(value)
        print(f"Found Valid Column: {response.name}")
        return True
    except ValueError:
        print("Invalid Column!")
        return False


def get_all_enum_values(*exclude_classes):
    all_values = []
    for cls in MarkerInterface.__subclasses__():
        if cls not in exclude_classes:
            all_values.extend([member.value for member in cls])
    return all_values
