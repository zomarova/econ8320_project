# NCS Hope Foundation Dashboard

This dashboard provides a live analysis of assistance applications using Streamlit and auto-refreshes every month.

## Files

- `data_cleaning.py`: Cleans the original Excel dataset
- `app.py`: Streamlit dashboard with five pages
- `.github/workflows/update_dashboard.yml`: Automates updates
- `NCSHF_Patient Assistance Dataset_Info for UNO SLA.xlsx`: Data dictionary only (not cleaned)

## Setup

```bash
pip install -r requirements.txt
python data_cleaning.py
streamlit run app.py
