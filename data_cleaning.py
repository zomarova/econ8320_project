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


# === Step 8: Save Cleaned File ===
output_file = "data/cleaned_data.csv"
df.to_csv(output_file, index=False)

print(f"Cleaned data saved to {output_file}")