import sys

from tonnage import build_report, export_report


def main():
    state = sys.argv[1]
    calendar_year = sys.argv[2] if len(sys.argv) > 2 else "2026"
    month = sys.argv[3] if len(sys.argv) > 3 else "08"

    result = build_report(state)
    print(result["report"])
    print(result["total_tonnage"])

    exports = export_report(
        result["report"],
        state,
        calendar_year,
        month,
        result["total_tonnage"],
    )
    print(f"Excel: {exports['excel_path']}")
    if exports["pdf_path"]:
        print(f"PDF: {exports['pdf_path']}")


if __name__ == "__main__":
    main()
