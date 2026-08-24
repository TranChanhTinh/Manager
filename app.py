import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hệ Thống Quản Lý Rack", layout="wide")

EXCEL_PATH = "RACK.xlsx"

# Sử dụng cache_resource cho đối tượng ExcelFile hoặc đọc danh sách sheet
@st.cache_resource
def get_excel_file():
    return pd.ExcelFile(EXCEL_PATH)

xls = get_excel_file()
sheets = xls.sheet_names

# 2. Thanh tìm kiếm & chọn Sheet
st.sidebar.title("🔍 Tìm kiếm & Tùy chọn")
selected_sheet = st.sidebar.selectbox("Chọn Sheet Rack:", sheets)
search_query = st.sidebar.text_input("Nhập mã sản phẩm/Rack:")

# Hàm đọc dữ liệu của từng Sheet (dùng cache_data an toàn cho DataFrame)
@st.cache_data
def load_sheet_data(sheet_name):
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=None).fillna("").astype(str)

df = load_sheet_data(selected_sheet)

# 3. Hiển thị sơ đồ Rack bằng Bảng HTML (Auto-fit toàn màn hình)
st.title(f"📦 Sơ đồ Rack: {selected_sheet}")

style = """
<style>
    .rack-table { width: 100%; border-collapse: collapse; text-align: center; table-layout: fixed; }
    .rack-table td { border: 1px solid #ccc; padding: 4px; font-size: 11px; font-weight: bold; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .tang3 { background-color: #f0aaf0; }
    .tang2 { background-color: #82c3eb; }
    .tang1 { background-color: #64dc64; }
    .khu   { background-color: #46b4e6; color: white; }
    .highlight { background-color: #ff0000 !important; color: white !important; font-size: 13px; }
</style>
"""
st.markdown(style, unsafe_allow_html=True)

html_code = "<table class='rack-table'>"
for r in range(df.shape[0]):
    html_code += "<tr>"
    for c in range(df.shape[1]):
        val = str(df.iloc[r, c]).strip()
        cell_class = ""
        
        if "Tang 3" in val: cell_class = "tang3"
        elif "Tang 2" in val: cell_class = "tang2"
        elif "Tang 1" in val: cell_class = "tang1"
        elif "Khu" in val: cell_class = "khu"
        
        if search_query and search_query.lower() in val.lower() and "tang" not in val.lower() and "khu" not in val.lower():
            cell_class += " highlight"

        disp_val = val[:8] if val else ""
        html_code += f"<td class='{cell_class}'>{disp_val}</td>"
    html_code += "</tr>"
html_code += "</table>"

st.markdown(html_code, unsafe_allow_html=True)
