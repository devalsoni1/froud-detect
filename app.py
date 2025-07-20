# 📁 Project: Credit Card Fraud Detection System (Beginner-Friendly)

# ---------------------------
# STEP 1: Library Imports
# ---------------------------
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
import os

# ---------------------------
# STEP 2: Streamlit Dashboard Setup
# ---------------------------
st.set_page_config(page_title="🛡️ Fraud Detector", layout="wide")
st.title("🛡️ Credit Card Fraud Detection")

# File upload section
uploaded_file = st.file_uploader("📤 Upload Transaction CSV File", type=["csv"])

# SQLite DB setup (if not exists)
db_path = "transactions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables if not exist
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    amount REAL,
    merchant TEXT,
    user_id INTEGER,
    category TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER,
    reason TEXT,
    timestamp TEXT
)''')
conn.commit()

# ---------------------------
# STEP 3: Helper Functions
# ---------------------------
def insert_transactions(df):
    df.to_sql("transactions", conn, if_exists='append', index=False)

def detect_fraud(df):
    alerts = []
    avg = df['amount'].mean()
    std_dev = df['amount'].std()
    threshold = avg + 2 * std_dev

    for _, row in df.iterrows():
        if row['amount'] > threshold:
            alerts.append({
                "transaction_id": row.get('id', None),
                "reason": f"High amount: ₹{row['amount']} (> ₹{threshold:.2f})",
                "timestamp": row['timestamp']
            })
    return pd.DataFrame(alerts)

# ---------------------------
# STEP 4: Main Pipeline
# ---------------------------
if uploaded_file:
    st.subheader("📄 Preview of Uploaded Data")
    df = pd.read_csv(uploaded_file)
    st.dataframe(df.head())

    # Clean missing values
    df = df.dropna(subset=['timestamp', 'amount', 'merchant', 'user_id'])

    # Insert clean data into DB
    insert_transactions(df)

    # Detect fraud using basic rule
    alerts_df = detect_fraud(df)

    # Save alerts
    if not alerts_df.empty:
        alerts_df.to_sql("alerts", conn, if_exists='append', index=False)
        st.warning(f"⚠️ {len(alerts_df)} suspicious transactions detected!")
        st.dataframe(alerts_df)
    else:
        st.success("✅ No suspicious activity detected.")

    # EDA section
    st.subheader("📊 Transaction Analysis")
    st.bar_chart(df.groupby(df['timestamp'].str[:10])["amount"].sum())
    st.bar_chart(df['merchant'].value_counts().head(10))

# ---------------------------
# STEP 5: Summary Dashboard
# ---------------------------
st.subheader("📦 Past Data Summary from Database")
txn_df = pd.read_sql("SELECT * FROM transactions", conn)
alert_df = pd.read_sql("SELECT * FROM alerts", conn)
st.metric("Total Transactions", len(txn_df))
st.metric("Total Alerts", len(alert_df))

# Show recent alerts
if not alert_df.empty:
    st.subheader("🚨 Recent Alerts")
    st.dataframe(alert_df.sort_values(by="timestamp", ascending=False).head(10))

conn.close()

st.markdown("---")
st.markdown("""
### 🎯 Why I Created This Project
This project was built to help detect fraudulent transactions in credit card data using basic statistical methods.""")
