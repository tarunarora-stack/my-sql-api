import streamlit as st
import psycopg2
import os
import pandas as pd

st.set_page_config(page_title="Product Manager", layout="wide")
st.title("📦 Product Management System")

def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def fetch_products():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM products ORDER BY id", conn)
    conn.close()
    return df

st.subheader("📋 Products")

try:
    df = fetch_products()
    if df.empty:
        st.info("No products found. Please add a product.")
    else:
        st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"Database error: {e}")
