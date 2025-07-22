import streamlit as st
import pandas as pd
import re

st.title("MN MFSAB Compliance Checker")

# Upload files
order_file = st.file_uploader("Upload Order Spreadsheet", type=["xlsx"])
state_spec_file = st.file_uploader("Upload State Spec Spreadsheet", type=["xlsx"])

def wildcard_to_regex(pattern):
    pattern = pattern.replace(".", r"\.")
    pattern = pattern.replace("XXX", r"\d{3}")
    pattern = pattern.replace("xx", r"\d{2}")
    pattern = pattern.replace("x", r"\d")
    pattern = pattern.replace("0x", r"0\d")
    pattern = pattern.replace(" ", "")
    return f"^{pattern}$"

def check_match(pattern, codes):
    try:
        regex = re.compile(wildcard_to_regex(str(pattern)))
        return any(regex.match(code) for code in codes)
    except re.error:
        return False

if order_file and state_spec_file:
    order_df = pd.read_excel(order_file, sheet_name="Mapics")
    state_spec_df = pd.read_excel(state_spec_file, sheet_name="MN", skiprows=9)

    # Clean up and rename columns
    state_spec_df.columns = [
        "Feature", "Source", "Option_Type_AI", "Option_Type_AII", "Option_MFSAB",
        "Option_Type_WC", "Revised_Date", "Revised_By", "Revision", "Unused1", "Unused2"
    ]

    # Filter MFSAB-required options
    mfsab_df = state_spec_df[
        state_spec_df["Option_MFSAB"].notna() & state_spec_df["Option_Type_AII"].notna()
    ]

    # Get clean lists
    required_patterns = mfsab_df["Option_Type_AII"].astype(str).str.strip()
    ordered_codes = order_df["Item Numbers"].dropna().astype(str).str.strip().tolist()

    # Match logic
    results = []
    for i, row in mfsab_df.iterrows():
        pattern = row["Option_Type_AII"]
        matched = check_match(pattern, ordered_codes)
        results.append({
            "Pattern": pattern,
            "Match Status": "✅ Matched" if matched else "❌ Missing",
            "Feature": row["Feature"],
            "Description": str(row["Source"])
        })

    result_df = pd.DataFrame(results)

    st.success("Compliance check complete.")
    st.dataframe(result_df)

    st.download_button(
        label="Download Updated Compliance Summary",
        data=result_df.to_csv(index=False).encode("utf-8"),
        file_name="Updated_MN_MFSAB_Compliance_Summary.csv",
        mime="text/csv"
    )
