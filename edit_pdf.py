from pathlib import Path
from datetime import date

from pypdf import PdfReader, PdfWriter


def edit_pdf(
    input_path,
    output_path,
    total_tonnage,
    calendar_year=None,
    month=None,
    report_date=None,
):
    """
    Fill Arkansas tonnage PDF form fields and write a new file.

    Fields filled: TotalTons, CalendarYear, Month, Date, InspectionFee
    """
    today = date.today()
    if calendar_year is None:
        calendar_year = today.year
    if month is None:
        month = today.strftime("%B")
    if report_date is None:
        report_date = today.strftime("%m/%d/%Y")

    reader = PdfReader(input_path)
    writer = PdfWriter(clone_from=reader)

    field_values = {
        "TotalTons": str(total_tonnage),
        "CalendarYear": str(calendar_year),
        "Month": str(month),
        "Date": str(report_date),
        "InspectionFee": str(round(total_tonnage * .375, 2))
    }

    for page in writer.pages:
        writer.update_page_form_field_values(page, field_values)

    writer.set_need_appearances_writer(True)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path
