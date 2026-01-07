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

# -------------------------------
# Add Product Section
# -------------------------------
st.subheader("➕ Add Product")

def add_product(name, price):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, price) VALUES (%s, %s)",
        (name, price)
    )
    conn.commit()
    conn.close()

with st.form("add_product_form"):
    name = st.text_input("Product Name")
    price = st.number_input("Price", min_value=0.0, step=0.01)
    submit = st.form_submit_button("Add Product")

    if submit:
        if name.strip() == "":
            st.warning("Product name cannot be empty")
        else:
            add_product(name, price)
            st.success("Product added successfully!")
            st.rerun()

try:
    df = fetch_products()
    if df.empty:
        st.info("No products found. Please add a product.")
    else:
        st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"Database error: {e}")
