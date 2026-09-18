from datetime import date
from pathlib import Path

import streamlit as st

from tonnage import PDF_TEMPLATES, build_report, export_report

st.set_page_config(page_title="Tonnage Report", layout="wide")

st.title("Tonnage Report")
st.caption("Build soil-amendment tonnage reports from CRM exports.")

MONTHS = [f"{i:02d}" for i in range(1, 13)]
MONTH_LABELS = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December",
}

with st.sidebar:
    st.header("Report settings")
    state = st.text_input("State code", value="AR", max_chars=2).upper().strip()
    calendar_year = st.text_input("Calendar year", value=str(date.today().year))
    month = st.selectbox(
        "Month",
        options=MONTHS,
        format_func=lambda m: f"{m} — {MONTH_LABELS[m]}",
        index=date.today().month - 1,
    )
    use_downloads = st.toggle(
        "Load from Downloads",
        value=True,
        help="Looks for ~/Downloads/Tonnage - {STATE}.csv",
    )
    uploaded = None
    if not use_downloads:
        uploaded = st.file_uploader("Upload CRM CSV", type=["csv"])

    save_desktop = st.toggle("Also save to Desktop", value=True)
    run = st.button("Run report", type="primary", use_container_width=True)

if run:
    csv_path = None
    temp_upload = None
    ok = False

    if use_downloads:
        csv_path = Path.home() / "Downloads" / f"Tonnage - {state}.csv"
        if not csv_path.exists():
            st.error(f"CSV not found: `{csv_path}`")
        else:
            ok = True
    else:
        if uploaded is None:
            st.error('Upload a CSV, or turn on "Load from Downloads".')
        else:
            temp_upload = Path.cwd() / f"_tonnage_upload_{state}.csv"
            temp_upload.write_bytes(uploaded.getvalue())
            csv_path = temp_upload
            ok = True

    if ok:
        try:
            result = build_report(state, csv_path=csv_path)
            output_dir = Path.home() / "Desktop" if save_desktop else Path.cwd() / "outputs"
            exports = export_report(
                result["report"],
                state,
                calendar_year,
                month,
                result["total_tonnage"],
                output_dir=output_dir,
            )
            st.session_state["last_result"] = result
            st.session_state["last_exports"] = exports
            st.session_state["last_meta"] = {
                "state": state,
                "calendar_year": calendar_year,
                "month": month,
            }
            st.success("Report generated.")
        except Exception as e:
            st.error(f"Failed to build report: {e}")
        finally:
            if temp_upload and temp_upload.exists():
                temp_upload.unlink(missing_ok=True)

if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    exports = st.session_state["last_exports"]
    meta = st.session_state["last_meta"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Input rows", result["input_rows"])
    m2.metric("Matched rows", result["matched_rows"])
    m3.metric("Total tonnage", result["total_tonnage"])
    m4.metric("Missing county", len(result["missing_county"]))

    st.subheader("Report")
    st.dataframe(result["report"], use_container_width=True)

    unmatched = result["unmatched"]
    if len(unmatched):
        st.warning(f"{len(unmatched)} row(s) did not match products.json")
        st.dataframe(unmatched, use_container_width=True)

    if len(result["missing_county"]):
        st.warning("Some rows are missing a county (bad or unknown zip).")
        st.dataframe(result["missing_county"], use_container_width=True)

    st.subheader("Downloads")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Download Excel",
            data=exports["excel_bytes"],
            file_name=(
                f"completed_tonnage-{meta['state']}-"
                f"{meta['month']}-{meta['calendar_year']}.xlsx"
            ),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
        if exports["excel_path"]:
            st.caption(f"Saved: `{exports['excel_path']}`")

    with c2:
        if exports["pdf_bytes"]:
            st.download_button(
                "Download PDF",
                data=exports["pdf_bytes"],
                file_name=(
                    f"{meta['state']}_Completed_Tonnage-"
                    f"{meta['month']}-{meta['calendar_year']}.pdf"
                ),
                mime="application/pdf",
                use_container_width=True,
            )
            if exports["pdf_path"]:
                st.caption(f"Saved: `{exports['pdf_path']}`")
        elif meta["state"] in PDF_TEMPLATES:
            st.info("PDF template is configured but was not generated.")
        else:
            st.info(f"No PDF template for `{meta['state']}` yet. Excel only.")
else:
    st.info("Set the state, month, and year in the sidebar, then click **Run report**.")
