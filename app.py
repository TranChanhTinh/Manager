import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hệ Thống Quản Lý Rack", layout="wide")

EXCEL_PATH = "RACK.xlsx"

@st.cache_resource
def get_excel_file():
    return pd.ExcelFile(EXCEL_PATH)

xls = get_excel_file()
sheets = xls.sheet_names

@st.cache_data
def load_sheet_data(sheet_name):
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=None).fillna("").astype(str)

# 1. Quản lý trạng thái Sheet và Ô đang được chọn
if "current_sheet" not in st.session_state:
    st.session_state.current_sheet = sheets[0]
if "selected_pos" not in st.session_state:
    st.session_state.selected_pos = None  # (row, col)

# 2. Thanh tìm kiếm bên trái
st.sidebar.title("🔍 Tìm kiếm & Tùy chọn")

# Tự động thay đổi Sheet trên Selectbox nếu người dùng click chọn từ Kết quả tìm kiếm
def on_sheet_change():
    st.session_state.current_sheet = st.sidebar.session_state.sheet_select_key
    st.session_state.selected_pos = None

st.sidebar.selectbox(
    "Chọn Sheet Rack:", 
    sheets, 
    key="sheet_select_key",
    index=sheets.index(st.session_state.current_sheet),
    on_change=on_sheet_change
)

search_query = st.sidebar.text_input("Nhập mã sản phẩm/Rack:", value="").strip()

# 3. Quét toàn bộ dữ liệu để tìm danh sách kết quả tương ứng
search_results = []
if search_query:
    for s_name in sheets:
        df_temp = load_sheet_data(s_name)
        for r in range(df_temp.shape[0]):
            for c in range(df_temp.shape[1]):
                val = df_temp.iloc[r, c].strip()
                if val and search_query.lower() in val.lower() and "tang" not in val.lower() and "khu" not in val.lower():
                    search_results.append({
                        "Sheet": s_name,
                        "Mã Hàng": val,
                        "Vị trí": f"Dòng {r+1}, Cột {c+1}",
                        "row": r,
                        "col": c
                    })

# 4. Hiển thị danh sách kết quả click-được
if search_query:
    st.sidebar.subheader(f"📋 Kết quả ({len(search_results)})")
    if search_results:
        # Tạo danh sách lựa chọn dạng Radio button hoặc Selectbox
        options = [f"[{item['Sheet']}] {item['Mã Hàng']} ({item['Vị trí']})" for item in search_results]
        
        selected_option = st.sidebar.radio("Click để trỏ tới vị trí:", options, index=0)
        
        # Cập nhật ngay lập tức Sheet và Vị trí ô tương ứng khi chọn
        selected_idx = options.index(selected_option)
        target = search_results[selected_idx]
        
        st.session_state.current_sheet = target["Sheet"]
        st.session_state.selected_pos = (target["row"], target["col"])
    else:
        st.sidebar.warning("Không tìm thấy kết quả phù hợp!")
else:
        st.session_state.selected_pos = None

# Đọc dữ liệu Sheet hiện tại
df = load_sheet_data(st.session_state.current_sheet)

# 5. Hiển thị sơ đồ Rack bằng Bảng HTML
st.title(f"📦 Sơ đồ Rack: {st.session_state.current_sheet}")

style = """
<style>
    .rack-table { width: 100%; border-collapse: collapse; text-align: center; table-layout: fixed; }
    .rack-table td { border: 1px solid #444; padding: 6px; font-size: 11px; font-weight: bold; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .tang3 { background-color: #f0aaf0; color: #000; }
    .tang2 { background-color: #82c3eb; color: #000; }
    .tang1 { background-color: #64dc64; color: #000; }
    .khu   { background-color: #46b4e6; color: white; }
    
    /* Vùng highlight nổi bật đỏ nhấp nháy cho ô được chọn */
    .highlight-active { 
        background-color: #ff0000 !important; 
        color: #ffffff !important; 
        font-size: 13px !important; 
        border: 2px solid #ffff00 !important;
        box-shadow: 0 0 10px #ff0000;
    }
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
        
        # Nếu trùng khớp với ô được người dùng click chọn từ danh sách tìm kiếm
        if st.session_state.selected_pos == (r, c):
            cell_class += " highlight-active"

        disp_val = val[:8] if val else ""
        html_code += f"<td class='{cell_class}'>{disp_val}</td>"
    html_code += "</tr>"
html_code += "</table>"

st.markdown(html_code, unsafe_allow_html=True)
