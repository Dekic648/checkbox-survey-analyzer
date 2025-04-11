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

    # Step 1: Select segmentation columns
    st.subheader("1️⃣ Choose columns to define segments")
    segment_cols = st.multiselect("Segment users by (combine columns)", options=[col for col in df.columns if df[col].nunique() < 30 and df[col].dtype == 'object'], default=[])

    # Step 2: Detect question blocks (checkbox-style by prefix)
    st.subheader("2️⃣ Select a checkbox-style question")
    checkbox_like_cols = [col for col in df.columns if df[col].notnull().sum() > 0 and df[col].dtype in ['float64', 'int64', 'object']]
    prefix_groups = {}
    for col in checkbox_like_cols:
        prefix = col.split(':')[0] if ':' in col else col.split(' ')[0]
        prefix_groups.setdefault(prefix, []).append(col)

    selected_prefix = st.selectbox("Select a question block (e.g. Q1, Q2, etc.)", options=list(prefix_groups.keys()))
    selected_checkbox_cols = prefix_groups[selected_prefix]

    if segment_cols and selected_checkbox_cols:
        st.subheader(f"📊 Compare Selections for Question: {selected_prefix}")

        # Create combined segment label
        df['CombinedSegment'] = df[segment_cols].astype(str).agg(' / '.join, axis=1)

        results = []
        for group, group_df in df.groupby('CombinedSegment'):
            total = len(group_df)
            for col in selected_checkbox_cols:
                count = group_df[col].notnull().sum()
                label = col.replace(selected_prefix + ':', '').strip()
                results.append({
                    'Segment': group,
                    'Option': label,
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
