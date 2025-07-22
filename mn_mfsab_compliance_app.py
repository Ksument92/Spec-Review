import streamlit as st
import pandas as pd
import re

st.title("MN MFSAB Compliance Checker")

# Upload files
order_file = st.file_uploader("Upload Order Spreadsheet", type=["xlsx"])
spec_file = st.file_uploader("Upload Pattern Spec CSV", type=["csv"])

# Convert wildcard pattern to regex
def wildcard_to_regex(pattern):
    pattern = pattern.replace(".", r"\.")
    pattern = pattern.replace("XXX", r"\d{3}")
    pattern = pattern.replace("xx", r"\d{2}")
    pattern = pattern.replace("x", r"\d")
    pattern = pattern.replace("0x", r"0\d")
    pattern = pattern.replace(" ", "")
    return f"^{pattern}$"

# Check if any code matches the pattern
def check_match(pattern, codes):
    try:
        regex = re.compile(wildcard_to_regex(str(pattern)))
        return any(regex.match(code) for code in codes)
    except re.error:
        return False

if order_file and spec_file:
    # Load order sheet and spec file
    order_df = pd.read_excel(order_file, sheet_name="Mapics")
    spec_df = pd.read_csv(spec_file)

    # Extract ordered codes
    ordered_codes = order_df["Item Numbers"].dropna().astype(str).str.strip().tolist()

    # Apply pattern matching
    spec_df["Match Status"] = spec_df["Pattern"].apply(
        lambda pat: "✅ Matched" if check_match(pat, ordered_codes) else "❌ Missing"
    )

    st.success("Compliance check complete.")

    # Show full results
    st.dataframe(spec_df)

    # Option to download updated file
    st.download_button(
        label="Download Updated Compliance Summary",
        data=spec_df.to_csv(index=False).encode("utf-8"),
        file_name="Updated_MN_MFSAB_Compliance_Summary.csv",
        mime="text/csv"
    )
