import streamlit as st
import psycopg2
import os
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Product Manager", layout="wide")
st.title("📦 Product Management System")

# -------------------------------
# Database Connection
# -------------------------------
def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])

# -------------------------------
# DB Operations
# -------------------------------
def fetch_products():
    conn = get_connection()
    df = pd.read_sql("SELECT id, name, price FROM products ORDER BY id", conn)
    conn.close()
    return df

def add_product(name, price):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, price) VALUES (%s, %s)",
        (name, price)
    )
    conn.commit()
    conn.close()

def update_product(pid, name, price):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE products SET name=%s, price=%s WHERE id=%s",
        (name, price, pid)
    )
    conn.commit()
    conn.close()

# -------------------------------
# Products Display
# -------------------------------
st.subheader("📋 Products")

df = fetch_products()

# Search
search = st.text_input("🔍 Search Product by Name")

if search:
    df = df[df["name"].str.contains(search, case=False, na=False)]

# Keep ID hidden for UI
df_display = df.copy()
df_display["Price"] = df_display["price"].apply(lambda x: f"₹ {x:,.2f}")
df_display = df_display.rename(columns={"name": "Product Name"})
df_display = df_display.drop(columns=["id", "price"])

if df_display.empty:
    st.info("No products found.")
else:
    st.dataframe(df_display, use_container_width=True)

# -------------------------------
# Export to Excel
# -------------------------------
def to_excel(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Products")
    return output.getvalue()

st.download_button(
    label="📤 Export to Excel",
    data=to_excel(df_display),
    file_name="products.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# -------------------------------
# Add Product
# -------------------------------
st.subheader("➕ Add Product")

with st.form("add_product_form", clear_on_submit=True):
    name = st.text_input("Product Name")
    price = st.number_input("Price", min_value=0.0, step=0.01)
    submit = st.form_submit_button("Add Product")

    if submit:
        if not name.strip():
            st.warning("Product name is required")
        else:
            add_product(name, price)
            st.success("Product added successfully!")
            st.rerun()

# -------------------------------
# Edit Product
# -------------------------------
st.subheader("✏ Edit Product")

if not df.empty:
    product_map = {
        f"{row.name} (₹ {row.price:,.2f})": row.id
        for _, row in df.iterrows()
    }

    selected = st.selectbox("Select Product", product_map.keys())
    selected_id = product_map[selected]

    selected_row = df[df["id"] == selected_id].iloc[0]

    with st.form("edit_product_form"):
        new_name = st.text_input("Product Name", selected_row["name"])
        new_price = st.number_input(
            "Price",
            min_value=0.0,
            step=0.01,
            value=float(selected_row["price"])
        )
        update = st.form_submit_button("Update Product")

        if update:
            update_product(selected_id, new_name, new_price)
            st.success("Product updated successfully!")
            st.rerun()
else:
    st.info("No products available to edit.")
