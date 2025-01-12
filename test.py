import pandas as pd


def calculate_taxable_from_final(final_amount, sgst_rate, cgst_rate):
    """
    Calculate taxable amount when given the final amount and GST rates
    """
    if sgst_rate == 0 and cgst_rate == 0:
        return final_amount
    total_gst_rate = (sgst_rate + cgst_rate) / 100
    taxable_amount = final_amount / (1 + total_gst_rate)
    return taxable_amount


def process_gst_data(input_file, output_file):
    # Read the Excel file
    df = pd.read_excel(input_file, header=None)

    # Create the output DataFrame with required columns
    output_columns = [
        'SR. No.', 'INVOICE NO.', 'INVOICE DATE', 'PARTY NAME', 'PARTY GST NO.',
        'STATE', 'PURCHASE 14%', 'SGST/IGST 14%', 'PURCHASE 9%', 'SGST/IGST 9%',
        'PURCHASE 6%', 'SGST/IGST 6%', 'PURCHASE 2.5%', 'SGST/IGST 2.5%',
        'TAXFREE', 'CGST 14%', 'CGST 9%', 'CGST 6%', 'CGST 2.5%', 'CRDRAMT',
        'OTHERADJ', 'LBTRS', 'CessRs', 'RNDOFF', 'TOTAL BILL AMOUNT'
    ]
    result_df = pd.DataFrame(columns=output_columns)

    def safe_float(value):
        """Convert value to float, handling various formats"""
        if pd.isna(value):
            return 0.0
        if isinstance(value, str):
            return float(value.replace(',', '').strip())
        return float(value)

    current_row = {}

    # Process each row
    i = 2  # Start from row 3 (index 2) to skip headers
    while i < len(df):
        row = df.iloc[i]

        # Check if this is a main row (has invoice number)
        if pd.notna(row[4]):  # Invoice number column
            if current_row:
                result_df = pd.concat([result_df, pd.DataFrame([current_row])], ignore_index=True)

            # Initialize new row with basic information
            current_row = {col: 0 for col in output_columns}
            current_row.update({
                'SR. No.': row[0],
                'PARTY NAME': row[1],
                'PARTY GST NO.': row[2],
                'INVOICE DATE': row[3],
                'INVOICE NO.': row[4],
                'TOTAL BILL AMOUNT': safe_float(row[5])
            })

        # Process GST information
        taxable_amount = safe_float(row[6])
        sgst_rate = safe_float(row[7])
        sgst_amount = safe_float(row[8])
        cgst_rate = safe_float(row[9])
        cgst_amount = safe_float(row[10])

        # Special case handling: When GST amounts are 0 but rates exist
        if ((sgst_rate > 0 and sgst_amount == 0) or
            (cgst_rate > 0 and cgst_amount == 0)) and taxable_amount > 0:
            # In this case, taxable_amount is actually the final amount including GST
            actual_taxable = calculate_taxable_from_final(taxable_amount, sgst_rate, cgst_rate)
            sgst_amount = actual_taxable * (sgst_rate / 100)
            cgst_amount = actual_taxable * (cgst_rate / 100)
            taxable_amount = actual_taxable

        # Map GST rates to corresponding columns
        if sgst_rate == 2.5 or cgst_rate == 2.5:
            current_row['PURCHASE 2.5%'] += taxable_amount
            current_row['SGST/IGST 2.5%'] += sgst_amount
            current_row['CGST 2.5%'] += cgst_amount
        elif sgst_rate == 6 or cgst_rate == 6:
            current_row['PURCHASE 6%'] += taxable_amount
            current_row['SGST/IGST 6%'] += sgst_amount
            current_row['CGST 6%'] += cgst_amount
        elif sgst_rate == 9 or cgst_rate == 9:
            current_row['PURCHASE 9%'] += taxable_amount
            current_row['SGST/IGST 9%'] += sgst_amount
            current_row['CGST 9%'] += cgst_amount
        elif sgst_rate == 14 or cgst_rate == 14:
            current_row['PURCHASE 14%'] += taxable_amount
            current_row['SGST/IGST 14%'] += sgst_amount
            current_row['CGST 14%'] += cgst_amount

        # Check if next row is a continuation (no invoice number)
        if i + 1 < len(df) and pd.isna(df.iloc[i + 1][4]):
            i += 1
        else:
            i += 1

    # Add the last row
    if current_row:
        result_df = pd.concat([result_df, pd.DataFrame([current_row])], ignore_index=True)

    # Format date column
    result_df['INVOICE DATE'] = pd.to_datetime(result_df['INVOICE DATE'], format='%d/%m/%Y').dt.strftime('%d/%m/%Y')

    # Round all numeric columns to 2 decimal places
    numeric_columns = [
        'PURCHASE 14%', 'SGST/IGST 14%', 'PURCHASE 9%', 'SGST/IGST 9%',
        'PURCHASE 6%', 'SGST/IGST 6%', 'PURCHASE 2.5%', 'SGST/IGST 2.5%',
        'CGST 14%', 'CGST 9%', 'CGST 6%', 'CGST 2.5%', 'TOTAL BILL AMOUNT'
    ]
    for col in numeric_columns:
        result_df[col] = result_df[col].round(2)

    # Write to Excel
    result_df.to_excel(output_file, index=False)


# Usage
if __name__ == "__main__":
    input_file = "4to11 test.xlsx"
    output_file = "processed_gst_data.xlsx"
    process_gst_data(input_file, output_file)