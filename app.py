import streamlit as st
import plotly.express as px


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

    # Format boolean into check/X marks
    display_df = review_df.copy()
    display_df["Ready_for_Review"] = display_df["Ready_for_Review"].apply(lambda x: "❌" if x else "✅")

    st.dataframe(display_df)


# === PAGE 2 ===
elif page == "📊 Support by Demographics":
    st.title("📊 Support Distribution by Demographics")

    # Mapping of user-friendly labels to column names
    demographic_options = {
        "City": "Pt_City",
        "State": "Pt_State",
        "Gender": "Gender",
        "Insurance Type": "Insurance_Type",
        "Application Year": "App_Year"
    }

    # Friendly dropdown
    selected_label = st.selectbox("Group By", list(demographic_options.keys()))
    demo_option = demographic_options[selected_label]

    # Create and display chart
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
    st.title("📋 Unused Grants and Assistance Types")

    if 'Remaining_Balance' in df.columns and 'App_Year' in df.columns:
        approved_df = df[
            (df['Request_Status'].str.lower() == 'approved') &
            df['Remaining_Balance'].notnull() &
            df['Amount'].notnull() &
            (df['Amount'] > 0)
        ]

        unused_df = approved_df[approved_df['Remaining_Balance'] > 0]

        # Debug check (optional)
        # st.write(unused_df.head())

        # 📈 Patients with unused support by year
        st.subheader("Patients with Unused Support by Year")
        count_by_year = unused_df.groupby('App_Year')['Patient_ID#'].nunique().reset_index()
        count_by_year.columns = ['Year', 'Patients']

        fig = px.bar(
            count_by_year,
            x='Year',
            y='Patients',
            text='Patients',
            color='Patients',
            color_continuous_scale='Reds'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            title={"text": "Number of Patients with Unused Grants by Year", "x": 0.5},
            plot_bgcolor='#0e1117',
            paper_bgcolor='#0e1117',
            font=dict(family='Arial', color='white', size=16),
            xaxis=dict(title="Application Year", showgrid=False, showline=True, linewidth=2, linecolor='white'),
            yaxis=dict(title="Number of Patients", showgrid=False, showline=True, linewidth=2, linecolor='white')
        )
        st.plotly_chart(fig)

        # 💰 Average support amount by assistance type
        st.subheader("Average Support Amount by Assistance Type")
        avg_support = approved_df.groupby('Type_of_Assistance_CLASS')['Amount'].mean().reset_index().dropna()
        avg_support.columns = ['Assistance Type', 'Support Amount ($)']

        fig2 = px.bar(
            avg_support,
            x='Support Amount ($)',
            y='Assistance Type',
            orientation='h',
            text='Support Amount ($)',
            color='Support Amount ($)',
            color_continuous_scale='Greens'
        )
        fig2.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig2.update_layout(
            title={"text": "Average Support Amount by Assistance Type", "x": 0.5},
            plot_bgcolor='#0e1117',
            paper_bgcolor='#0e1117',
            font=dict(family='Arial', color='white', size=16),
            xaxis=dict(title="Average Amount ($)", showgrid=False, showline=True, linewidth=2, linecolor='white'),
            yaxis=dict(title="Assistance Type", showgrid=False, showline=True, linewidth=2, linecolor='white')
        )
        st.plotly_chart(fig2)

    else:
        st.warning("Required columns for this analysis are missing.")


# === PAGE 5 ===
elif page == "📈 Annual Impact Summary":
    st.title("Foundation Impact Summary")

    # Filter approved entries
    approved_df = df[df['Request_Status'].str.lower() == 'approved'].copy()

    # Clean strings
    approved_df['Type_of_Assistance_CLASS'] = approved_df['Type_of_Assistance_CLASS'].astype(str).str.strip().str.title()

    # Clean city names
    approved_df['Pt_City'] = approved_df['Pt_City'].replace('nan', pd.NA)
    approved_df = approved_df.dropna(subset=['Pt_City'])

    # Key stats
    total_patients = approved_df['Patient_ID#'].nunique()
    total_support = approved_df['Amount'].sum()
    avg_support = approved_df['Amount'].mean()
    common_assistance = approved_df['Type_of_Assistance_CLASS'].mode().iloc[0] if 'Type_of_Assistance_CLASS' in approved_df else 'N/A'
    avg_days = approved_df['Days_To_Support'].mean() if 'Days_To_Support' in approved_df else None

    # Show top-level metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Patients Helped", f"{total_patients}")
    col2.metric("Total Support Given", f"${total_support:,.2f}")
    col3.metric("Average Support", f"${avg_support:,.2f}")

    col4, col5 = st.columns(2)
    col4.metric("Most Common Assistance Type", common_assistance)
    if avg_days is not None:
        col5.metric("⏱️ Avg Days to Support", f"{avg_days:.1f} days")
    else:
        col5.metric("⏱️ Avg Days to Support", "N/A")

    # 📈 Trend Line
    if 'App_Year' in approved_df.columns:
        trend_df = approved_df.groupby('App_Year').agg({
            'Amount': 'sum',
            'Patient_ID#': pd.Series.nunique
        }).reset_index().rename(columns={
            'App_Year': 'Year',
            'Amount': 'Total Support',
            'Patient_ID#': 'Unique Patients'
        })

        st.subheader("Total Support Trend by Year")
        fig = px.line(trend_df, x='Year', y='Total Support', markers=True, title="Total Support Given by Year")
        fig.update_layout(
            plot_bgcolor='#0e1117',
            paper_bgcolor='#0e1117',
            font=dict(family='Arial', color='white', size=16),
            xaxis=dict(title='Year', showline=True, linewidth=2, linecolor='white'),
            yaxis=dict(title='Total Support ($)', showline=True, linewidth=2, linecolor='white')
        )
        st.plotly_chart(fig)
