import streamlit as st
import pandas as pd

# Thiết lập trang tràn màn hình
st.set_page_config(page_title="Hệ Thống Quản Lý Rack Kho", layout="wide", initial_sidebar_state="expanded")

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

# 2. Tự động tiêm CSS giao diện Modern Dashboard
custom_css = """
<style>
    /* Bảng màu tối UI Chuyên nghiệp */
    .stApp { background-color: #0e1117; }
    
    /* Tùy chỉnh thanh Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    
    /* Card thống kê KPI */
    .kpi-card {
        background: #1f242d;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 16px;
        color: #f0f6fc;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .kpi-title { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { font-size: 18px; font-weight: 700; color: #58a6ff; margin-top: 2px; }

    /* Thiết kế Bảng Rack UI */
    .rack-container {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        margin-top: 10px;
        overflow-x: auto;
    }
    
    .rack-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 3px;
        table-layout: fixed;
    }
    
    .rack-table td {
        border-radius: 4px;
        padding: 8px 2px;
        font-size: 11px;
        font-weight: 600;
        text-align: center;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        transition: all 0.2s ease-in-out;
        color: #c9d1d9;
        background-color: #21262d;
    }
    
    .rack-table td:hover {
        transform: scale(1.04);
        z-index: 10;
        box-shadow: 0 0 8px rgba(255,255,255,0.3);
    }

    /* Các phân vùng màu */
    .tang3 { background-color: #d946ef !important; color: #ffffff !important; }
    .tang2 { background-color: #0284c7 !important; color: #ffffff !important; }
    .tang1 { background-color: #16a34a !important; color: #ffffff !important; }
    .khu   { background-color: #f59e0b !important; color: #ffffff !important; font-weight: 800; }
    .empty-cell { background-color: #0d1117 !important; opacity: 0.4; }

    /* Ô đang được Active / Chọn */
    .highlight-active { 
        background-color: #dc2626 !important; 
        color: #ffffff !important; 
        font-size: 12px !important; 
        border: 2px solid #facc15 !important;
        animation: pulse 1.2s infinite alternate;
    }

    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.7); }
        100% { transform: scale(1.06); box-shadow: 0 0 12px 4px rgba(250, 204, 21, 0.8); }
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 3. Thanh bên Sidebar
st.sidebar.markdown("<h2 style='color:#58a6ff; font-size:20px; margin-bottom:0;'>📦 WMS RACK SYSTEM</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color:#8b949e; font-size:12px;'>Hệ thống quản lý định vị kho</p>", unsafe_allow_html=True)
st.sidebar.divider()

def on_sheet_change():
    st.session_state.current_sheet = st.sidebar.session_state.sheet_select_key
    st.session_state.selected_pos = None

st.sidebar.selectbox(
    "📍 Chọn Khung Rack (Sheet):", 
    sheets, 
    key="sheet_select_key",
    index=sheets.index(st.session_state.current_sheet),
    on_change=on_sheet_change
)

search_query = st.sidebar.text_input("🔍 Tìm nhanh mã vị trí / hàng:", value="", placeholder="Ví dụ: ML-138...").strip()

# 4. Thu thập dữ liệu tìm kiếm
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
        st.sidebar.warning("Trùng khớp 0 kết quả.")
else:
    st.session_state.selected_pos = None

# Đọc dữ liệu Sheet hiện tại
df = load_sheet_data(st.session_state.current_sheet)

# 5. Header Dashboard + KPI Cards
total_cells = df.shape[0] * df.shape[1]
occupied_cells = sum((df.iloc[r, c].strip() != "" and "tang" not in df.iloc[r, c].lower() and "khu" not in df.iloc[r, c].lower()) for r in range(df.shape[0]) for c in range(df.shape[1]))

c1, c2, c3, c4 = st.columns([3, 2, 2, 2])

with c1:
    st.markdown(f"<h2 style='color:#f0f6fc; margin:0;'>Sơ Đồ Rack: <span style='color:#58a6ff;'>{st.session_state.current_sheet}</span></h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#8b949e; font-size:13px; margin:0;'>Kích thước: {df.shape[0]} Dòng × {df.shape[1]} Cột</p>", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Tổng số ô</div>
        <div class="kpi-value" style="color:#c9d1d9;">{total_cells}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Số ô đã lưu trữ</div>
        <div class="kpi-value">{occupied_cells}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    occupancy_rate = round((occupied_cells / total_cells) * 100, 1) if total_cells > 0 else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Tỷ lệ lấp đầy</div>
        <div class="kpi-value" style="color:#2ba640;">{occupancy_rate}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# 6. Dựng ma trận sơ đồ Rack
html_code = "<div class='rack-container'><table class='rack-table'>"
for r in range(df.shape[0]):
    html_code += "<tr>"
    for c in range(df.shape[1]):
        val = str(df.iloc[r, c]).strip()
        cell_class = ""
        
        if "Tang 3" in val: cell_class = "tang3"
        elif "Tang 2" in val: cell_class = "tang2"
        elif "Tang 1" in val: cell_class = "tang1"
        elif "Khu" in val: cell_class = "khu"
        elif not val: cell_class = "empty-cell"
        
        if st.session_state.selected_pos == (r, c):
            cell_class += " highlight-active"

        disp_val = val[:10] if val else ""
        html_code += f"<td class='{cell_class}' title='Dòng {r+1}, Cột {c+1}: {val}'>{disp_val}</td>"
    html_code += "</tr>"
html_code += "</table></div>"

st.markdown(html_code, unsafe_allow_html=True)
