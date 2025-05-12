import pandas as pd
import numpy as np
import os

# === Load Files ===
data_file = "data/UNO Service Learning Data Sheet De-Identified Version.xlsx"

# Load data
df = pd.read_excel(data_file)

# === Step 1: Standardize Column Names ===
df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")

# === Step 2: Convert Dates ===
df['Grant_Req_Date'] = pd.to_datetime(df['Grant_Req_Date'], errors='coerce')

# === Step 3: Replace "Missing" with NaN ===
df.replace("Missing", np.nan, inplace=True)

# === Step 4: Clean Categorical Fields ===
cat_cols = ['Request_Status', 'Payment_Submitted?', 'Application_Signed?']
for col in cat_cols:
    df[col] = df[col].astype(str).str.strip().str.lower()

# === Step 5: Convert Amount Columns ===
amount_cols = ['Amount', 'Remaining_Balance']
for col in amount_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# === Step 6: Create Flags or Derived Columns ===
df['Ready_for_Review'] = (df['Request_Status'] == 'approved') & (df['Application_Signed?'] != 'yes')

# === Step 7: Simulate variable support sent delays (normal distribution) ===
np.random.seed(42)  # for reproducibility
delays = np.random.normal(loc=7, scale=2, size=len(df)).round().astype(int)
delays = np.clip(delays, 1, None)  # ensure minimum delay is 1 day

df["Days_To_Support"] = delays
df["Support_Sent_Date"] = df["Grant_Req_Date"] + pd.to_timedelta(df["Days_To_Support"], unit="D")

# === Step 8: Normalize demographic text columns ===
# === Step 8: Clean and normalize demographic fields ===

# Function to standardize text columns
def clean_column(col):
    return col.astype(str).str.strip().str.title()

# --- Clean Gender ---
df["Gender"] = clean_column(df["Gender"])
df["Gender"] = df["Gender"].replace({
    "Transgender Female": "Other",
    "Transgender Fem...": "Other",
    "Other (Write In)": "Other",
    "Unknown": "Other",
    "Nan": "Other"
})
df["Gender"] = df["Gender"].fillna("Other")  # Ensure no NaNs

# --- Clean Pt_State ---
df["Pt_State"] = df["Pt_State"].astype(str).str.strip().str.upper()
df = df[df["Pt_State"] != "NAN"]  # Remove missing state entries

# --- Clean Insurance_Type ---
# --- Clean Insurance_Type ---
df["Insurance_Type"] = clean_column(df["Insurance_Type"])

df["Insurance_Type"] = df["Insurance_Type"].replace({
    "No Insurance": "Uninsured",
    "None": "Uninsured",
    "N/A": "Uninsured",
    "Uninsurred": "Uninsured",
    "Uninsurerd": "Uninsured",
    "Unisured": "Uninsured",
    "Private Insurance": "Private",
    "Medicare & Private": "Medicare",
    "Medicare & Other": "Medicare",
    "Medicaid & Medicare": "Medicare",
    "Medicaid & Medic...": "Medicare",
    "Healthcare.Gov": "Other",
    "Military Program": "Other",
    "Unknown": "Other",
    "Missing": "Other",
    "Nan": "Other"
})

df["Insurance_Type"] = df["Insurance_Type"].fillna("Other")



# === Step 9: Save Cleaned File ===
output_file = "data/cleaned_data.csv"
df.to_csv(output_file, index=False)

print(f"Cleaned data saved to {output_file}")
