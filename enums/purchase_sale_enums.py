from enum import Enum
from enums.VoucherEnums import SalesRate, PurchaseRate, TaxRate

class RateInterface(Enum):
    ...

    @classmethod
    def get_all_string_values(cls):
        return [member.value for member in cls]



class PurchaseRate28(RateInterface):
    PURCHASE_28_PERCENT = PurchaseRate.PURCHASE_28_PERCENT.value
    CGST_28_PERCENT = TaxRate.CGST_28_PERCENT.value
    SGST_28_PERCENT = TaxRate.SGST_28_PERCENT.value


class PurchaseRate18(RateInterface):
    PURCHASE_18_PERCENT = PurchaseRate.PURCHASE_18_PERCENT.value
    CGST_18_PERCENT = TaxRate.CGST_18_PERCENT.value
    SGST_18_PERCENT = TaxRate.SGST_18_PERCENT.value


class PurchaseRate12(RateInterface):
    PURCHASE_12_PERCENT = PurchaseRate.PURCHASE_12_PERCENT.value
    CGST_12_PERCENT = TaxRate.CGST_12_PERCENT.value
    SGST_12_PERCENT = TaxRate.SGST_12_PERCENT.value


class PurchaseRate5(RateInterface):
    PURCHASE_5_PERCENT = PurchaseRate.PURCHASE_5_PERCENT.value
    CGST_5_PERCENT = TaxRate.CGST_5_PERCENT.value
    SGST_5_PERCENT = TaxRate.SGST_5_PERCENT.value


class SaleRate28(RateInterface):
    SALES_28_PERCENT = SalesRate.SALES_28_PERCENT.value
    CGST_28_PERCENT = TaxRate.CGST_28_PERCENT.value
    SGST_28_PERCENT = TaxRate.SGST_28_PERCENT.value


class SaleRate18(RateInterface):
    SALES_18_PERCENT = SalesRate.SALES_18_PERCENT.value
    CGST_18_PERCENT = TaxRate.CGST_18_PERCENT.value
    SGST_18_PERCENT = TaxRate.SGST_18_PERCENT.value


class SaleRate12(RateInterface):
    SALES_12_PERCENT = SalesRate.SALES_12_PERCENT.value
    CGST_12_PERCENT = TaxRate.CGST_12_PERCENT.value
    SGST_12_PERCENT = TaxRate.SGST_12_PERCENT.value


class SaleRate5(RateInterface):
    SALES_5_PERCENT = SalesRate.SALES_5_PERCENT.value
    CGST_5_PERCENT = TaxRate.CGST_5_PERCENT.value
    SGST_5_PERCENT = TaxRate.SGST_5_PERCENT.value


string_enum_mapping = {
    "Purchase@28%": PurchaseRate28,
    "Purchase@18%": PurchaseRate18,
    "Purchase@12%": PurchaseRate12,
    "Purchase@5%": PurchaseRate5,
    "Sales@28%": SaleRate28,
    "Sales@18%": SaleRate18,
    "Sales@12%": SaleRate12,
    "Sales@5%": SaleRate5,
}
