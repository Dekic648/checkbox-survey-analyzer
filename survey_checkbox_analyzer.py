
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Survey Checkbox Analyzer", layout="wide")
st.title("📊 Survey Checkbox Analyzer")

uploaded_file = st.file_uploader("Upload your survey Excel or CSV file", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("🔍 Preview of Uploaded Data")
    st.dataframe(df.head())

    # Step 1: Select segmentation field
    st.subheader("1️⃣ Select a field to segment users")
    segment_col = st.selectbox("Segment by", options=[col for col in df.columns if df[col].nunique() < 30 and df[col].dtype == 'object'])

    # Step 2: Detect checkbox columns (bool or True/False like)
    st.subheader("2️⃣ Select checkbox question columns")
    checkbox_cols = st.multiselect("Select checkbox question columns", options=[col for col in df.columns if df[col].dropna().isin([True, False]).all()])

    if segment_col and checkbox_cols:
        st.subheader("📊 Charts of Checkbox Selections by Segment")

        results = []
        for group, group_df in df.groupby(segment_col):
            for col in checkbox_cols:
                count = group_df[col].sum()
                total = len(group_df)
                results.append({
                    segment_col: group,
                    'Option': col.replace("Q_Values_", ""),
                    'Count': count,
                    'Percent': round(100 * count / total, 1)
                })

        chart_df = pd.DataFrame(results)

        chart = alt.Chart(chart_df).mark_bar().encode(
            x=alt.X('Option:N', title='Selected Value'),
            y=alt.Y('Percent:Q', title='Selected (%)'),
            color=segment_col + ':N',
            column=alt.Column(segment_col + ':N', title=segment_col)
        ).properties(height=300).interactive()

        st.altair_chart(chart, use_container_width=True)
        st.dataframe(chart_df)

        st.download_button("Download Table as CSV", chart_df.to_csv(index=False), file_name="segmented_checkbox_summary.csv")
else:
    st.info("Upload a CSV or Excel file to get started.")
