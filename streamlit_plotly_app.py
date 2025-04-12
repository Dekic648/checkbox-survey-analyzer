
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Survey Checkbox Analyzer", layout="wide")
st.title("📊 Survey Checkbox Analyzer")

uploaded_file = st.file_uploader("Upload your survey Excel or CSV file", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df_raw = pd.read_csv(uploaded_file, header=None)
    else:
        df_raw = pd.read_excel(uploaded_file, header=None)

    question_row = df_raw.iloc[0]
    header_row = df_raw.iloc[1]
    data = df_raw[2:].copy()
    data.columns = header_row.astype(str)

    st.subheader("🔍 Preview of Uploaded Data")
    st.dataframe(data.head())

    st.subheader("1️⃣ Choose columns to define segments")
    segment_candidates = [col for col in data.columns if data[col].nunique() < 30 and data[col].dtype == 'object']
    segment_cols = st.multiselect("Segment users by (combine columns)", options=segment_candidates, default=[])

    st.subheader("2️⃣ Select a question to analyze")
    excluded_cols = set(segment_cols + ['UserID'])
    question_map = {}
    for idx, col in enumerate(data.columns):
        question = str(question_row[idx]) if idx < len(question_row) else "Unknown"
        if col not in excluded_cols and question not in ["", "nan"]:
            question_map.setdefault(question, []).append(col)

    if not question_map:
        st.warning("No valid question blocks found. Please check your file format.")
    else:
        selected_question = st.selectbox("Select a question block", options=list(question_map.keys()))
        selected_checkbox_cols = question_map[selected_question]

        if segment_cols and selected_checkbox_cols:
            st.subheader(f"📊 Compare Selections for Question: {selected_question}")

            data['CombinedSegment'] = data[segment_cols].astype(str).agg(' / '.join, axis=1)

            results = []
            for group, group_df in data.groupby('CombinedSegment'):
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

            fig = px.bar(
                chart_df,
                x="Option",
                y="Percent",
                color="Segment",
                barmode="group",
                text="Percent",
                color_discrete_sequence=px.colors.qualitative.Set2,
                labels={"Percent": "Checked (%)"},
                title=f"📊 {selected_question} by Segment"
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                yaxis=dict(range=[0, 100]),
                plot_bgcolor="white",
                font=dict(family="Arial", size=14),
                xaxis_title="Option",
                margin=dict(t=50, l=40, r=40, b=50)
            )

            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(chart_df)

            st.download_button("Download Table as CSV", chart_df.to_csv(index=False), file_name="question_block_segment_comparison.csv")
else:
    st.info("Upload a CSV or Excel file to get started.")
