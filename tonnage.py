from pathlib import Path
from io import BytesIO

import pandas as pd
import zipcodes
from openpyxl.utils import get_column_letter

import edit_pdf
from config import *

PROJECT_DIR = Path(__file__).resolve().parent
PDF_TEMPLATES = {
    "AR": PROJECT_DIR / "AR_Tonnage_Template.pdf",
}


def read_csv(state, csv_path=None):
    if csv_path is None:
        csv_path = Path.home() / "Downloads" / f"Tonnage - {state}.csv"
    return pd.read_csv(csv_path)


def mergeJSON(products):
    products_df = pd.read_json(PROJECT_DIR / JSON_FILE_STR, orient="index")
    products_df = products_df.reset_index().rename(columns={"index": PRODUCT_NAME_STR})
    merged_df = products.merge(products_df, on=PRODUCT_NAME_STR)
    unmatched = products[~products[PRODUCT_NAME_STR].isin(products_df[PRODUCT_NAME_STR])]
    return merged_df, unmatched


def calculate_tonnage(merged_df):
    grouped_products = (
        merged_df.groupby(
            [
                PRODUCT_NAME_STR,
                SHIPPING_CODE_STR,
                SHIPPING_CITY_STR,
                PACKAGE_SIZE_STR,
                POUNDS_PER_GALLON_STR,
                NPK_STR,
            ]
        )[QUANTITY_STR]
        .sum()
        .reset_index()
    )
    package_size = grouped_products[PACKAGE_SIZE_STR]
    pounds_per_gallon = grouped_products[POUNDS_PER_GALLON_STR]
    quantity = grouped_products[QUANTITY_STR]
    total_weight = round((package_size * pounds_per_gallon * quantity) / 2000, 3)
    grouped_products[TONNAGE_STR] = total_weight
    return grouped_products


def add_county_from_zip(df):
    def lookup(z):
        matches = zipcodes.matching(str(z))
        return matches[0]["county"] if matches else None

    df = df.copy()
    df[COUNTY_STR] = df[SHIPPING_CODE_STR].apply(lookup)
    return df


def dataframe_to_excel_bytes(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
        ws = writer.sheets["Sheet1"]
        for col_idx, col_name in enumerate(df.columns, start=1):
            max_len = max(
                len(str(col_name)),
                *(len(str(val)) for val in df[col_name].astype(str)),
            )
            ws.column_dimensions[get_column_letter(col_idx)].width = max_len + 2
    return buffer.getvalue()


def to_excel(df, state, calendar_year, month, output_dir=None):
    if output_dir is None:
        output_dir = Path.home() / "Desktop"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = output_dir / f"completed_tonnage-{state}-{month}-{calendar_year}.xlsx"
    filename.write_bytes(dataframe_to_excel_bytes(df))
    return filename


def build_report(state, csv_path=None):
    products = read_csv(state, csv_path=csv_path)
    combined_df, unmatched = mergeJSON(products)
    report = calculate_tonnage(combined_df)
    report = add_county_from_zip(report)
    total_tonnage = round(report[TONNAGE_STR].sum(), 3)
    missing_county = report[report[COUNTY_STR].isna()]
    return {
        "report": report,
        "unmatched": unmatched,
        "total_tonnage": total_tonnage,
        "missing_county": missing_county,
        "input_rows": len(products),
        "matched_rows": len(combined_df),
    }


def export_report(report, state, calendar_year, month, total_tonnage, output_dir=None):
    if output_dir is None:
        output_dir = Path.home() / "Desktop"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    excel_path = to_excel(report, state, calendar_year, month, output_dir=output_dir)
    pdf_path = None
    pdf_bytes = None

    template = PDF_TEMPLATES.get(state)
    if template and template.exists():
        pdf_path = output_dir / f"{state}_Completed_Tonnage-{month}-{calendar_year}.pdf"
        edit_pdf.edit_pdf(
            template,
            pdf_path,
            total_tonnage=total_tonnage,
            calendar_year=calendar_year,
            month=month,
        )
        pdf_bytes = Path(pdf_path).read_bytes()

    return {
        "excel_path": excel_path,
        "excel_bytes": dataframe_to_excel_bytes(report),
        "pdf_path": pdf_path,
        "pdf_bytes": pdf_bytes,
    }
