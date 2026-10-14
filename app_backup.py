
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from src.analysis import analyze_results

st.set_page_config(
    page_title="Student Result Intelligence",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Result Intelligence")
st.caption("Student Performance Analytics & Early Risk Identification")

uploaded_file = st.file_uploader(
    "Upload student data (CSV or Excel)",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        required = [
            "Maths", "Science", "English", "Computer"
        ]

        missing = [c for c in required if c not in df.columns]

        if missing:
            st.error(f"Required subject columns missing: {missing}")
            st.stop()

        for col in required:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=required)

        if df.empty:
            st.error("No valid student marks found.")
            st.stop()

        if ((df[required] < 0) | (df[required] > 100)).any().any():
            st.warning("Some marks are outside the expected 0–100 range.")

        result = analyze_results(df)

        st.success("Student data analyzed successfully!")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Students", len(result))
        c2.metric("Pass Students", int((result["Result"] == "Pass").sum()))
        c3.metric("Fail Students", int((result["Result"] == "Fail").sum()))
        c4.metric("Average Percentage", f"{result['Percentage'].mean():.2f}%")

        st.subheader("📋 Student Result Details")
        st.dataframe(result, use_container_width=True)

        left, right = st.columns(2)

        with left:
            st.subheader("Performance Distribution")
            counts = result["Performance_Level"].value_counts().reset_index()
            counts.columns = ["Performance", "Students"]
            fig = px.bar(
                counts, x="Performance", y="Students",
                color="Performance", title="Student Performance Levels"
            )
            st.plotly_chart(fig, use_container_width=True)

        with right:
            st.subheader("Subject Average Marks")
            averages = result[required].mean().reset_index()
            averages.columns = ["Subject", "Average Marks"]
            fig = px.bar(
                averages, x="Subject", y="Average Marks",
                title="Average Marks by Subject", range_y=[0, 100]
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("⚠️ Students Requiring Attention")
        risk = result[
            (result["Percentage"] < 50) |
            (result["Result"] == "Fail")
        ]
        st.dataframe(risk, use_container_width=True)

        csv = result.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Analyzed Results",
            data=csv,
            file_name="student_analysis_results.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Could not process the file: {e}")

else:
    st.info("Upload a CSV or Excel file to start student performance analysis.")

    sample_path = Path("data/student_results.csv")
    if sample_path.exists():
        if st.button("Analyze Included Sample Dataset"):
            st.session_state["use_sample"] = True

    if st.session_state.get("use_sample", False):
        result = analyze_results(pd.read_csv(sample_path))
        st.dataframe(result, use_container_width=True)
        st.metric("Average Percentage", f"{result['Percentage'].mean():.2f}%")
