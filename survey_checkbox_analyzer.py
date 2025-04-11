import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Survey Checkbox Analyzer", layout="wide")
st.title("📊 Survey Checkbox Analyzer")

uploaded_file = st.file_uploader("Upload your survey Excel or CSV file", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df_raw = pd.read_csv(uploaded_file, header=None)
    else:
        df_raw = pd.read_excel(uploaded_file, header=None)

    # Extract question blocks from the first row, keep the rest as data
    question_row = df_raw.iloc[0]
    df = df_raw[1:].copy()
    df.columns = df_raw.iloc[1] if df_raw.iloc[1].isnull().sum() == 0 else df_raw.columns
    df.columns = df.columns.astype(str)

    st.subheader("🔍 Preview of Uploaded Data")
    st.dataframe(df.head())

    # Step 1: Select segmentation columns
    st.subheader("1️⃣ Choose columns to define segments")
    segment_cols = st.multiselect("Segment users by (combine columns)", options=[col for col in df.columns if df[col].nunique() < 30 and df[col].dtype == 'object'], default=[])

    # Step 2: Group columns by question block from row 0
    st.subheader("2️⃣ Select a checkbox-style question")
    excluded_cols = set(segment_cols + ['UserID'])
    checkbox_columns = [col for col in df.columns if col not in excluded_cols and df[col].notnull().sum() > 0]
    question_map = {}
    for idx, col in enumerate(df.columns):
        question = str(question_row[idx]) if idx < len(question_row) else "Unknown"
        if col not in excluded_cols and question != 'nan':
            question_map.setdefault(question, []).append(col)

    if not question_map:
        st.warning("No valid checkbox-style question blocks found. Please check your file format.")
    else:
        selected_question = st.selectbox("Select a question block", options=list(question_map.keys()))
        selected_checkbox_cols = question_map[selected_question]

        if segment_cols and selected_checkbox_cols:
            st.subheader(f"📊 Compare Selections for Question: {selected_question}")

            # Create combined segment label
            df['CombinedSegment'] = df[segment_cols].astype(str).agg(' / '.join, axis=1)

            results = []
            for group, group_df in df.groupby('CombinedSegment'):
                total = len(group_df)
                for col in selected_checkbox_cols:
                    count = group_df[col].notnull().sum()
                    results.append({
                        'Segment': group,
                        'Option': col,
                        'Count': count,
                        'Percent': round(100 * count / total, 1) if total else 0
                    })

            chart_df = pd.DataFrame(results)

            chart = alt.Chart(chart_df).mark_bar().encode(
                x=alt.X('Option:N', title='Option'),
                y=alt.Y('Percent:Q', title='Checked (%)'),
                color='Segment:N'
            ).properties(height=400).interactive()

            st.altair_chart(chart, use_container_width=True)
            st.dataframe(chart_df)

            st.download_button("Download Table as CSV", chart_df.to_csv(index=False), file_name="question_block_segment_comparison.csv")
else:
    st.info("Upload a CSV or Excel file to get started.")
