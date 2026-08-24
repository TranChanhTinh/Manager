import streamlit as st
import pandas as pd

st.set_page_config(page_title="Quản Lý Rack Kho - Excel Style", layout="wide", initial_sidebar_state="expanded")

EXCEL_PATH = "RACK.xlsx"

@st.cache_resource
def get_excel_file():
    return pd.ExcelFile(EXCEL_PATH)

xls = get_excel_file()
sheets = xls.sheet_names

@st.cache_data
def load_sheet_data(sheet_name):
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=None).fillna("").astype(str)

# 1. Khởi tạo trạng thái Session
if "current_sheet" not in st.session_state:
    st.session_state.current_sheet = sheets[0]
if "selected_pos" not in st.session_state:
    st.session_state.selected_pos = None

# 2. CSS phong cách Microsoft Excel Classic
excel_css = """
<style>
    /* Nền ứng dụng màu xám sáng chuẩn Office */
    .stApp { background-color: #f3f3f3; }
    
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #d1d1d1;
    }

    /* Container chứa bảng Excel */
    .excel-container {
        background: #ffffff;
        border: 1px solid #c8c8c8;
        padding: 0;
        margin-top: 10px;
        overflow-x: auto;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .excel-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        font-family: "Segoe UI", Arial, sans-serif;
    }
    
    /* Đường lưới ô Excel */
    .excel-table td, .excel-table th {
        border: 1px solid #d4d4d4;
        padding: 4px 2px;
        font-size: 11px;
        text-align: center;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        color: #000000;
        background-color: #ffffff;
    }

    /* Header tiêu đề Cột A, B, C... và Dòng 1, 2, 3... */
    .excel-header {
        background-color: #e6e6e6 !important;
        color: #333333 !important;
        font-weight: 600 !important;
        font-size: 10px !important;
        user-select: none;
    }

    /* Màu sắc theo phân vùng tầng / khu */
    .tang3 { background-color: #f0aaf0 !important; color: #000000 !important; font-weight: bold; }
    .tang2 { background-color: #82c3eb !important; color: #000000 !important; font-weight: bold; }
    .tang1 { background-color: #64dc64 !important; color: #000000 !important; font-weight: bold; }
    .khu   { background-color: #46b4e6 !important; color: #ffffff !important; font-weight: bold; }

    /* Ô khi được tìm thấy / chọn */
    .highlight-active { 
        background-color: #ff0000 !important; 
        color: #ffffff !important; 
        font-size: 11px !important; 
        font-weight: bold !important;
        border: 2px solid #000000 !important;
        animation: excel-flash 1s infinite alternate;
    }

    @keyframes excel-flash {
        0% { background-color: #ff0000; color: #ffffff; }
        100% { background-color: #ffff00; color: #000000; }
    }
</style>
"""
st.markdown(excel_css, unsafe_allow_html=True)

# 3. Thanh bên Sidebar
st.sidebar.markdown("<h3 style='color:#107c41; margin-bottom:0;'>📊 EXCEL RACK VIEW</h3>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color:#666666; font-size:12px;'>Hệ thống tra cứu định vị kho</p>", unsafe_allow_html=True)
st.sidebar.divider()

def on_sheet_change():
    st.session_state.current_sheet = st.session_state.sheet_select_key
    st.session_state.selected_pos = None

st.sidebar.selectbox(
    "📍 Chọn Trang (Sheet):", 
    sheets, 
    key="sheet_select_key",
    index=sheets.index(st.session_state.current_sheet),
    on_change=on_sheet_change
)

search_query = st.sidebar.text_input("🔍 Tìm mã sản phẩm / Rack:", value="", placeholder="Ví dụ: ML-138...").strip()

# 4. Tìm kiếm dữ liệu
search_results = []
if search_query:
    for s_name in sheets:
        df_temp = load_sheet_data(s_name)
        for r in range(df_temp.shape[0]):
            for c in range(df_temp.shape[1]):
                val = df_temp.iloc[r, c].strip()
                if val and search_query.lower() in val.lower() and "tang" not in val.lower() and "khu" not in val.lower():
                    # Chuyển đổi chỉ số cột sang dạng chữ cái Excel (A, B, C... Z, AA...)
                    col_letter = chr(65 + c) if c < 26 else f"{chr(65 + c//26 - 1)}{chr(65 + c%26)}"
                    search_results.append({
                        "Sheet": s_name,
                        "Mã Hàng": val,
                        "Vị trí": f"Tọa độ ({col_letter}{r+1}) - Dòng {r+1}, Cột {c+1}",
                        "row": r,
                        "col": c
                    })

if search_query:
    st.sidebar.markdown(f"<b>Kết quả tìm kiếm ({len(search_results)})</b>", unsafe_allow_html=True)
    if search_results:
        options = [f"[{item['Sheet']}] {item['Mã Hàng']} — {item['Vị trí']}" for item in search_results]
        selected_option = st.sidebar.radio("Click chọn để di chuyển tới:", options, index=0)
        
        selected_idx = options.index(selected_option)
        target = search_results[selected_idx]
        
        st.session_state.current_sheet = target["Sheet"]
        st.session_state.selected_pos = (target["row"], target["col"])
    else:
        st.sidebar.warning("Không tìm thấy dữ liệu khớp.")
else:
    st.session_state.selected_pos = None

# Đọc dữ liệu Sheet hiện tại
df = load_sheet_data(st.session_state.current_sheet)

# 5. Tiêu đề hiển thị chuẩn Sheet Excel
st.markdown(f"<h3 style='color:#107c41; margin:0;'>Sheet: #{st.session_state.current_sheet} <span style='color:#555; font-size:15px; font-weight:normal;'>({df.shape[0]}x{df.shape[1]} cells)</span></h3>", unsafe_allow_html=True)

# 6. Dựng ma trận bảng tính Excel chuẩn
html_code = "<div class='excel-container'><table class='excel-table'>"

# Dòng tiêu đề Tên Cột (A, B, C, D...)
html_code += "<tr><th class='excel-header' style='width: 35px;'></th>"
for c in range(df.shape[1]):
    col_letter = chr(65 + c) if c < 26 else f"{chr(65 + c//26 - 1)}{chr(65 + c%26)}"
    html_code += f"<th class='excel-header'>{col_letter}</th>"
html_code += "</tr>"

# Dựng các hàng ô dữ liệu kèm Số Dòng (1, 2, 3...)
for r in range(df.shape[0]):
    html_code += f"<tr><td class='excel-header'>{r+1}</td>"
    for c in range(df.shape[1]):
        val = str(df.iloc[r, c]).strip()
        cell_class = ""
        
        if "Tang 3" in val: cell_class = "tang3"
        elif "Tang 2" in val: cell_class = "tang2"
        elif "Tang 1" in val: cell_class = "tang1"
        elif "Khu" in val: cell_class = "khu"
        
        if st.session_state.selected_pos == (r, c):
            cell_class += " highlight-active"

        disp_val = val if val else ""
        html_code += f"<td class='{cell_class}' title='Dòng {r+1}, Cột {c+1}: {val}'>{disp_val}</td>"
    html_code += "</tr>"
html_code += "</table></div>"

st.markdown(html_code, unsafe_allow_html=True)
