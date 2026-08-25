import streamlit as st
import pandas as pd

st.set_page_config(page_title="WMS Cyber Rack Management", layout="wide", initial_sidebar_state="expanded")

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

# 2. CSS Dark Glassmorphism & Neon UI (Đã tăng độ sáng và tương phản)
cyber_css = """
<style>
    /* Nền đen sâu & Tùy chỉnh Sidebar */
    .stApp { background-color: #0b0f19; }
    
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1f2937;
    }

    /* Thẻ Thống Kê KPI Glassmorphism */
    .kpi-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 12px 18px;
        color: #f8fafc;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    .kpi-title { font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600; }
    .kpi-value { font-size: 20px; font-weight: 800; color: #38bdf8; margin-top: 2px; text-shadow: 0 0 10px rgba(56, 189, 248, 0.4); }

    /* Khung chứa sơ đồ Rack */
    .rack-container {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-top: 10px;
        overflow-x: auto;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
    }
    
    .rack-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 5px;
        table-layout: fixed;
        font-family: 'JetBrains Mono', 'Fira Code', 'Segoe UI', monospace;
    }
    
    .rack-table td {
        border-radius: 6px;
        padding: 10px 4px;
        font-size: 11px;
        font-weight: 700;
        text-align: center;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        color: #cbd5e1;
        background-color: #1e293b;
        border: 1px solid #475569;
    }
    
    .rack-table td:hover {
        transform: translateY(-2px) scale(1.05);
        z-index: 50;
        box-shadow: 0 5px 20px rgba(56, 189, 248, 0.6);
        border-color: #38bdf8 !important;
        color: #ffffff !important;
    }

    /* Các phân vùng màu Neon sắc nét, sáng rõ hơn */
    .tang3 { 
        background: linear-gradient(135deg, #c026d3 0%, #a855f7 100%) !important; 
        color: #ffffff !important; 
        border: 1px solid #f0abfc !important;
        box-shadow: 0 0 10px rgba(217, 70, 239, 0.4);
    }
    .tang2 { 
        background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%) !important; 
        color: #ffffff !important; 
        border: 1px solid #7dd3fc !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
    }
    .tang1 { 
        background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%) !important; 
        color: #ffffff !important; 
        border: 1px solid #86efac !important;
        box-shadow: 0 0 10px rgba(74, 222, 128, 0.4);
    }
    .khu { 
        background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%) !important; 
        color: #ffffff !important; 
        font-weight: 900; 
        border: 1px solid #fde68a !important;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.4);
        letter-spacing: 0.5px;
    }
    .empty-cell { 
        background-color: #131c2e !important; 
        border: 1px dashed #334155 !important; 
        color: #475569 !important;
    }

    /* Hiệu ứng nhấp nháy Neon cho ô chọn */
    .highlight-active { 
        background: #f43f5e !important; 
        color: #ffffff !important; 
        font-size: 12px !important; 
        border: 2px solid #38bdf8 !important;
        animation: cyber-pulse 1s infinite alternate;
        z-index: 100;
    }

    @keyframes cyber-pulse {
        0% { transform: scale(1); box-shadow: 0 0 12px #f43f5e, 0 0 20px #38bdf8; }
        100% { transform: scale(1.08); box-shadow: 0 0 20px #f43f5e, 0 0 35px #38bdf8; }
    }
</style>
"""
st.markdown(cyber_css, unsafe_allow_html=True)

# 3. Sidebar điều hướng
st.sidebar.markdown("<h2 style='color:#38bdf8; font-size:22px; font-weight:800; margin-bottom:0;'>⚡ RACK CYBER TTL</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color:#94a3b8; font-size:12px;'>Hệ thống tra cứu & định vị kho thông minh</p>", unsafe_allow_html=True)
st.sidebar.divider()

def on_sheet_change():
    st.session_state.current_sheet = st.session_state.sheet_select_key
    st.session_state.selected_pos = None

st.sidebar.selectbox(
    "📍 Chọn Khung Rack (Sheet):", 
    sheets, 
    key="sheet_select_key",
    index=sheets.index(st.session_state.current_sheet),
    on_change=on_sheet_change
)

search_query = st.sidebar.text_input("🔍 Tìm nhanh mã vị trí / hàng:", value="", placeholder="Ví dụ: ML-138...").strip()

# 4. Tìm kiếm dữ liệu
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
    st.sidebar.markdown(f"<b style='color:#38bdf8;'>Kết quả tìm kiếm ({len(search_results)})</b>", unsafe_allow_html=True)
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

# 5. Dashboard Stats Header
total_cells = df.shape[0] * df.shape[1]
occupied_cells = sum((df.iloc[r, c].strip() != "" and "tang" not in df.iloc[r, c].lower() and "khu" not in df.iloc[r, c].lower()) for r in range(df.shape[0]) for c in range(df.shape[1]))

c1, c2, c3, c4 = st.columns([3, 2, 2, 2])

with c1:
    st.markdown(f"<h2 style='color:#f8fafc; margin:0;'>Sơ Đồ Rack: <span style='color:#38bdf8; text-shadow:0 0 10px rgba(56,189,248,0.4);'>{st.session_state.current_sheet}</span></h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#94a3b8; font-size:13px; margin:0;'>Kích thước ma trận: {df.shape[0]} Dòng × {df.shape[1]} Cột</p>", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Tổng số vị trí</div>
        <div class="kpi-value" style="color:#f8fafc;">{total_cells}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Đã lưu trữ</div>
        <div class="kpi-value">{occupied_cells}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    occupancy_rate = round((occupied_cells / total_cells) * 100, 1) if total_cells > 0 else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Tỷ lệ lấp đầy</div>
        <div class="kpi-value" style="color:#4ade80;">{occupancy_rate}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

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
