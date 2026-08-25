import streamlit as st
import pandas as pd

st.set_page_config(page_title="WMS Cyber Rack Management", layout="wide", initial_sidebar_state="expanded")

EXCEL_PATH = "RACK.xlsx"

# Hàm đọc dữ liệu không dùng cache để luôn cập nhật tức thì
def get_excel_file():
    return pd.ExcelFile(EXCEL_PATH)

def load_sheet_data(sheet_name):
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=None).fillna("").astype(str)

xls = get_excel_file()
sheets = xls.sheet_names

# 1. Khởi tạo trạng thái Session
if "current_sheet" not in st.session_state:
    st.session_state.current_sheet = sheets[0]
if "selected_pos" not in st.session_state:
    st.session_state.selected_pos = None

# 2. CSS Dark Glassmorphism & Neon UI
cyber_css = """
<style>
    .stApp { background-color: #0b0f19; }
    
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1f2937;
    }

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

# ==========================================
# ⚙️ MÔ-ĐỦN QUẢN LÝ TƯƠNG TÁC DỮ LIỆU REAL-TIME (CRUD)
# ==========================================
st.sidebar.divider()
st.sidebar.markdown("<h3 style='color:#38bdf8; font-size:16px; margin-bottom:0;'>🛠️ Quản Lý Vị Trí / Thùng Hàng</h3>", unsafe_allow_html=True)

# Hàm ghi dữ liệu cập nhật vào file Excel
def save_all_sheets_data(sheets_dict):
    with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl') as writer:
        for s_name, df_data in sheets_dict.items():
            df_data.to_excel(writer, sheet_name=s_name, index=False, header=False)

crud_action = st.sidebar.selectbox("Thao tác:", ["Thêm / Cập nhật", "Di chuyển", "Xóa / Xuất hàng"])

c_r, c_c = st.sidebar.columns(2)
with c_r:
    row_idx = st.number_input("Dòng (Row)", min_value=1, max_value=df.shape[0], value=1) - 1
with c_c:
    col_idx = st.number_input("Cột (Col)", min_value=1, max_value=df.shape[1], value=1) - 1

if crud_action == "Thêm / Cập nhật":
    current_val = df.iloc[row_idx, col_idx]
    new_val = st.sidebar.text_input("Mã thùng / Nội dung mới:", value=current_val)
    if st.sidebar.button("💾 Luu Cập Nhật", use_container_width=True):
        # Đọc tất cả sheet để lưu lại toàn bộ Workbook
        all_sheets = {s: load_sheet_data(s) for s in sheets}
        all_sheets[st.session_state.current_sheet].iloc[row_idx, col_idx] = new_val
        save_all_sheets_data(all_sheets)
        st.sidebar.success(f"Đã cập nhật tại Dòng {row_idx+1}, Cột {col_idx+1}")
        st.rerun()

elif crud_action == "Di chuyển":
    st.sidebar.caption("Di chuyển tới vị trí đích:")
    t_sheet = st.sidebar.selectbox("Sheet đích:", sheets, index=sheets.index(st.session_state.current_sheet))
    df_target = load_sheet_data(t_sheet)
    
    tc_r, tc_c = st.sidebar.columns(2)
    with tc_r:
        t_row = st.number_input("Dòng đích", min_value=1, max_value=df_target.shape[0], value=1) - 1
    with tc_c:
        t_col = st.number_input("Cột đích", min_value=1, max_value=df_target.shape[1], value=1) - 1
        
    if st.sidebar.button("🚚 Di Chuyển Hàng", use_container_width=True):
        all_sheets = {s: load_sheet_data(s) for s in sheets}
        val_to_move = all_sheets[st.session_state.current_sheet].iloc[row_idx, col_idx]
        
        if not val_to_move.strip():
            st.sidebar.error("Vị trí nguồn đang trống!")
        else:
            # Chuyển giá trị
            all_sheets[st.session_state.current_sheet].iloc[row_idx, col_idx] = ""
            all_sheets[t_sheet].iloc[t_row, t_col] = val_to_move
            save_all_sheets_data(all_sheets)
            st.sidebar.success(f"Đã chuyển '{val_to_move}' thành công!")
            st.rerun()

elif crud_action == "Xóa / Xuất hàng":
    if st.sidebar.button("🗑️ Xuất Hàng Khỏi Vị Trí", use_container_width=True):
        all_sheets = {s: load_sheet_data(s) for s in sheets}
        all_sheets[st.session_state.current_sheet].iloc[row_idx, col_idx] = ""
        save_all_sheets_data(all_sheets)
        st.sidebar.success(f"Đã xóa hàng tại Dòng {row_idx+1}, Cột {col_idx+1}")
        st.rerun()

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
