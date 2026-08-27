import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="WMS Cyber Rack Management", layout="wide", initial_sidebar_state="expanded")

EXCEL_PATH = "RACK.xlsx"

# ==========================================
# ⚙️ QUẢN LÝ DỮ LIỆU & CACHE OPTIMIZATION
# ==========================================
@st.cache_data
def get_all_sheet_names():
    if not os.path.exists(EXCEL_PATH):
        st.error(f"Không tìm thấy file: {EXCEL_PATH}")
        st.stop()
    with pd.ExcelFile(EXCEL_PATH) as xls:
        return xls.sheet_names

@st.cache_data
def load_sheet_data(sheet_name):
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=None).fillna("").astype(str)

def save_all_sheets_data(sheets_dict):
    """Ghi đè tất cả các sheet dữ liệu vào file Excel và làm mới Cache"""
    try:
        with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl') as writer:
            for s_name, df_data in sheets_dict.items():
                df_data.to_excel(writer, sheet_name=s_name, index=False, header=False)
        # Invalidate Cache sau khi ghi dữ liệu thành công
        st.cache_data.clear()
        return True, "Cập nhật dữ liệu thành công!"
    except PermissionError:
        return False, "File Excel đang được mở bởi chương trình khác. Vui lòng đóng file và thử lại!"
    except Exception as e:
        return False, f"Lỗi không xác định: {str(e)}"

sheets = get_all_sheet_names()

# 1. Khởi tạo Session State
if "current_sheet" not in st.session_state:
    st.session_state.current_sheet = sheets[0]
if "selected_pos" not in st.session_state:
    st.session_state.selected_pos = None

# 2. CSS Dark Glassmorphism & Neon UI
cyber_css = """
<style>
    .stApp { background-color: #0b0f19; }
    section[data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid #1f2937; }

    .kpi-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid #334155; border-radius: 10px; padding: 12px 18px; color: #f8fafc;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    .kpi-title { font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600; }
    .kpi-value { font-size: 20px; font-weight: 800; color: #38bdf8; margin-top: 2px; text-shadow: 0 0 10px rgba(56, 189, 248, 0.4); }

    .rack-container {
        background: #0f172a; border: 1px solid #334155; border-radius: 12px;
        padding: 16px; margin-top: 10px; overflow-x: auto; box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
    }
    .rack-table {
        width: 100%; border-collapse: separate; border-spacing: 4px;
        table-layout: fixed; font-family: 'JetBrains Mono', 'Fira Code', 'Segoe UI', monospace;
    }
    .rack-table td {
        border-radius: 6px; padding: 10px 2px; font-size: 11px; font-weight: 700;
        text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
        transition: all 0.2s ease-in-out; color: #cbd5e1; background-color: #1e293b; border: 1px solid #334155;
    }
    .lbl-khu { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important; color: #ffffff !important; font-weight: 900; border: 1px solid #fde68a !important; }
    .lbl-tang3 { background: linear-gradient(135deg, #c026d3 0%, #a855f7 100%) !important; color: #ffffff !important; font-weight: 800; border: 1px solid #f0abfc !important; }
    .lbl-tang2 { background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%) !important; color: #ffffff !important; font-weight: 800; border: 1px solid #7dd3fc !important; }
    .lbl-tang1 { background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%) !important; color: #ffffff !important; font-weight: 800; border: 1px solid #86efac !important; }

    .item-tang3 { background: rgba(192, 38, 211, 0.18) !important; color: #f5d0fe !important; border: 1px solid rgba(232, 121, 249, 0.5) !important; }
    .item-tang2 { background: rgba(2, 132, 199, 0.18) !important; color: #bae6fd !important; border: 1px solid rgba(56, 189, 248, 0.5) !important; }
    .item-tang1 { background: rgba(22, 163, 74, 0.18) !important; color: #bbf7d0 !important; border: 1px solid rgba(74, 222, 128, 0.5) !important; }

    .empty-cell { background-color: #0b1329 !important; border: 1px dashed #1e293b !important; color: #334155 !important; }
    .highlight-active { background: #f43f5e !important; color: #ffffff !important; border: 2px solid #38bdf8 !important; animation: cyber-pulse 1s infinite alternate; z-index: 100; }

    @keyframes cyber-pulse {
        0% { transform: scale(1); box-shadow: 0 0 12px #f43f5e, 0 0 20px #38bdf8; }
        100% { transform: scale(1.08); box-shadow: 0 0 20px #f43f5e, 0 0 35px #38bdf8; }
    }
</style>
"""
st.markdown(cyber_css, unsafe_allow_html=True)

# 3. Sidebar Navigation & Search
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

df = load_sheet_data(st.session_state.current_sheet)

# 4. Thuật toán xác định bản đồ Khu
zone_map = {} 
current_zone = ""
for c in range(df.shape[1]):
    for r in range(df.shape[0]):
        val = str(df.iloc[r, c]).strip()
        if "khu" in val.lower():
            current_zone = val
            break
    zone_map[c] = current_zone

# 5. Tìm kiếm dữ liệu đa sheet
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
        st.sidebar.warning("Không tìm thấy kết quả phù hợp.")

df = load_sheet_data(st.session_state.current_sheet)

# ==========================================
# 🛠️ MODULE QUẢN LÝ TƯƠNG TÁC DỮ LIỆU (CRUD)
# ==========================================
st.sidebar.divider()
st.sidebar.markdown("<h3 style='color:#38bdf8; font-size:16px; margin-bottom:0;'>🛠️ Quản Lý Vị Trí / Thùng Hàng</h3>", unsafe_allow_html=True)

crud_action = st.sidebar.selectbox("Thao tác:", ["Thêm / Cập nhật", "Di chuyển", "Xóa / Xuất hàng"])

c_r, c_c = st.sidebar.columns(2)
with c_r:
    default_r = st.session_state.selected_pos[0] + 1 if st.session_state.selected_pos else 1
    row_idx = st.number_input("Dòng (Row)", min_value=1, max_value=df.shape[0], value=default_r) - 1
with c_c:
    default_c = st.session_state.selected_pos[1] + 1 if st.session_state.selected_pos else 1
    col_idx = st.number_input("Cột (Col)", min_value=1, max_value=df.shape[1], value=default_c) - 1

if crud_action == "Thêm / Cập nhật":
    current_val = df.iloc[row_idx, col_idx]
    new_val = st.sidebar.text_input("Mã thùng / Nội dung mới:", value=current_val)
    if st.sidebar.button("💾 Lưu Cập Nhật", use_container_width=True):
        all_sheets = {s: load_sheet_data(s).copy() for s in sheets}
        all_sheets[st.session_state.current_sheet].iloc[row_idx, col_idx] = new_val
        
        success, msg = save_all_sheets_data(all_sheets)
        if success:
            st.sidebar.success(msg)
            st.rerun()
        else:
            st.sidebar.error(msg)

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
        all_sheets = {s: load_sheet_data(s).copy() for s in sheets}
        val_to_move = all_sheets[st.session_state.current_sheet].iloc[row_idx, col_idx]
        
        if not val_to_move.strip():
            st.sidebar.error("Vị trí nguồn đang trống!")
        else:
            all_sheets[st.session_state.current_sheet].iloc[row_idx, col_idx] = ""
            all_sheets[t_sheet].iloc[t_row, t_col] = val_to_move
            
            success, msg = save_all_sheets_data(all_sheets)
            if success:
                st.sidebar.success(f"Đã chuyển '{val_to_move}' thành công!")
                st.rerun()
            else:
                st.sidebar.error(msg)

elif crud_action == "Xóa / Xuất hàng":
    if st.sidebar.button("🗑️ Xuất Hàng Khỏi Vị Trí", use_container_width=True, type="primary"):
        all_sheets = {s: load_sheet_data(s).copy() for s in sheets}
        all_sheets[st.session_state.current_sheet].iloc[row_idx, col_idx] = ""
        
        success, msg = save_all_sheets_data(all_sheets)
        if success:
            st.sidebar.success(f"Đã xóa hàng tại Dòng {row_idx+1}, Cột {col_idx+1}")
            st.rerun()
        else:
            st.sidebar.error(msg)

# 6. Dashboard Header & Export Feature
total_cells = df.shape[0] * df.shape[1]
occupied_cells = sum((df.iloc[r, c].strip() != "" and "tang" not in df.iloc[r, c].lower() and "khu" not in df.iloc[r, c].lower()) for r in range(df.shape[0]) for c in range(df.shape[1]))

c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
with c1:
    st.markdown(f"<h2 style='color:#f8fafc; margin:0;'>Sơ Đồ Rack: <span style='color:#38bdf8; text-shadow:0 0 10px rgba(56,189,248,0.4);'>{st.session_state.current_sheet}</span></h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#94a3b8; font-size:13px; margin:0;'>Kích thước ma trận: {df.shape[0]} Dòng × {df.shape[1]} Cột</p>", unsafe_allow_html=True)

with c2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Tổng số vị trí</div><div class="kpi-value" style="color:#f8fafc;">{total_cells}</div></div>', unsafe_allow_html=True)

with c3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Đã lưu trữ</div><div class="kpi-value">{occupied_cells}</div></div>', unsafe_allow_html=True)

with c4:
    occupancy_rate = round((occupied_cells / total_cells) * 100, 1) if total_cells > 0 else 0
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Tỷ lệ lấp đầy</div><div class="kpi-value" style="color:#4ade80;">{occupancy_rate}%</div></div>', unsafe_allow_html=True)

# Tải xuống Báo cáo File Excel
with open(EXCEL_PATH, "rb") as f:
    st.download_button(
        label="📥 Tải Báo Cáo Excel Hiện Tại",
        data=f,
        file_name="RACK_WMS_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# 7. Render Sơ Đồ Ma Trận
html_code = "<div class='rack-container'><table class='rack-table'>"
current_tier = "" 

for r in range(df.shape[0]):
    row_vals = [str(df.iloc[r, c]).strip() for c in range(df.shape[1])]
    for val in row_vals:
        if "tang 3" in val.lower(): current_tier = "Tang 3"
        elif "tang 2" in val.lower(): current_tier = "Tang 2"
        elif "tang 1" in val.lower(): current_tier = "Tang 1"

    html_code += "<tr>"
    for c in range(df.shape[1]):
        val = str(df.iloc[r, c]).strip()
        cell_class = ""
        zone_info = zone_map.get(c, "")
        
        if "tang 3" in val.lower(): cell_class = "lbl-tang3"
        elif "tang 2" in val.lower(): cell_class = "lbl-tang2"
        elif "tang 1" in val.lower(): cell_class = "lbl-tang1"
        elif "khu" in val.lower(): cell_class = "lbl-khu"
        elif not val: 
            cell_class = "empty-cell"
        else:
            if current_tier == "Tang 3": cell_class = "item-tang3"
            elif current_tier == "Tang 2": cell_class = "item-tang2"
            elif current_tier == "Tang 1": cell_class = "item-tang1"

        if st.session_state.selected_pos == (r, c):
            cell_class += " highlight-active"

        disp_val = val[:10] if val else ""
        tooltip_text = f"{zone_info} | {current_tier} | Dòng {r+1}, Cột {c+1}"
        if val and "tang" not in val.lower() and "khu" not in val.lower():
            tooltip_text += f": {val}"

        html_code += f"<td class='{cell_class}' title='{tooltip_text}'>{disp_val}</td>"
    html_code += "</tr>"
html_code += "</table></div>"

st.markdown(html_code, unsafe_allow_html=True)
