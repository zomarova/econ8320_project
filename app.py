import streamlit as st

# MUST BE FIRST Streamlit COMMAND
st.set_page_config(page_title="NCS Hope Foundation Dashboard", layout="wide")

import pandas as pd


# Load cleaned data
@st.cache_data
def load_data():
    return pd.read_csv("data/cleaned_data.csv", parse_dates=["Grant_Req_Date"])


df = load_data()

# Sidebar navigation
page = st.sidebar.selectbox(
    "Dashboard Pages",
    [
        "📋 Ready for Review",
        "📊 Support by Demographics",
        "⏱️ Time to Support",
        "💸 Grant Usage & Budgeting",
        "📈 Annual Impact Summary"
    ]
)

# === PAGE 1 ===
if page == "📋 Ready for Review":
    st.title("📋 Applications Ready for Review")
    signed_filter = st.selectbox("Application Signed?", ["all", "yes", "no"])

    review_df = df[df["Request_Status"] == "approved"]
    if signed_filter != "all":
        review_df = review_df[review_df["Application_Signed?"] == signed_filter]

    st.dataframe(review_df)

# === PAGE 2 ===
elif page == "📊 Support by Demographics":
    st.title("📊 Support Distribution by Demographics")
    demo_option = st.selectbox("Group By", ["Pt_City", "Pt_State", "Gender", "Income", "Insurance_Type", "App_Year"])

    if demo_option in df.columns:
        summary = df.groupby(demo_option)["Amount"].sum().reset_index()
        st.bar_chart(summary.set_index(demo_option))


# === PAGE 3 ===
elif page == "⏱️ Time to Support":
    st.title("⏱️ Time Between Request and Support Sent")

    if "Days_To_Support" in df.columns:
        st.metric("Average Days to Support", round(df["Days_To_Support"].mean(), 2))
        st.bar_chart(df["Days_To_Support"].value_counts().sort_index())
        st.write(df[["Grant_Req_Date", "Support_Sent_Date", "Days_To_Support"]].head(10))
    else:
        st.warning("Support sent date is not available or needs to be computed.")

# === PAGE 4 ===
elif page == "💸 Grant Usage & Budgeting":
    st.title("💸 Grant Usage and Budgeting")
    df["Unused_Amount"] = df["Remaining_Balance"]

    unused_by_year = df.groupby("App_Year")["Unused_Amount"].sum().reset_index()
    avg_by_type = df.groupby("Type_of_Assistance_CLASS")["Amount"].mean().reset_index()

    st.subheader("Unused Grant Amounts by Application Year")
    st.bar_chart(unused_by_year.set_index("App_Year"))

    st.subheader("Average Support Amount by Assistance Type")
    st.dataframe(avg_by_type)

# === PAGE 5 ===
elif page == "📈 Annual Impact Summary":
    st.title("📈 Annual Impact Summary")

    yearly_stats = df.groupby("App_Year").agg(
        Total_Applications=("Patient_ID#", "nunique"),
        Total_Support_Amount=("Amount", "sum"),
        Avg_Grant_Per_Patient=("Amount", "mean")
    ).reset_index()

    st.write("Impact Summary by Year")
    st.dataframe(yearly_stats)
