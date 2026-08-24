import cv2
import numpy as np
import pandas as pd
import time

EXCEL_PATH = "RACK.xlsx"
xls = pd.ExcelFile(EXCEL_PATH)
sheets = xls.sheet_names

current_sheet_idx = 0
search_text = ""
highlight_pos = None  # (row, col)

search_results = []
selected_result_idx = -1

# Kích thước màn hình OpenCV
WIN_W, WIN_H = 1360, 720
RACK_VIEW_W = 930      
PANEL_RIGHT_X = 950    

MARGIN_X, MARGIN_Y = 10, 80
VIEW_W = RACK_VIEW_W - MARGIN_X - 10
VIEW_H = WIN_H - MARGIN_Y - 10

# Bảng màu BGR
COLOR_TANG3 = (235, 170, 240)
COLOR_TANG2 = (235, 195, 130)
COLOR_TANG1 = (100, 220, 100)
COLOR_KHU   = (230, 180, 70)

EXCEL_HEADER_BG = (210, 230, 210)
EXCEL_GRID_BORDER = (220, 220, 220)
EXCEL_SELECT_ROW = (200, 225, 255)

def load_data(sheet_name):
    df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=None)
    return df.fillna("").astype(str).values

grid_data = load_data(sheets[current_sheet_idx])

def update_global_search(query):
    global search_results, selected_result_idx
    search_results.clear()
    selected_result_idx = -1
    query = query.strip().lower()
    if not query:
        return
        
    for s_idx, s_name in enumerate(sheets):
        data = load_data(s_name)
        for r in range(data.shape[0]):
            for c in range(data.shape[1]):
                val = data[r, c].strip()
                if val and query in val.lower() and "tang" not in val.lower() and "khu" not in val.lower():
                    search_results.append({
                        "sheet_idx": s_idx,
                        "sheet_name": s_name,
                        "row": r,
                        "col": c,
                        "val": val
                    })

def select_result_item(idx):
    global current_sheet_idx, grid_data, highlight_pos, selected_result_idx
    if 0 <= idx < len(search_results):
        selected_result_idx = idx
        res = search_results[idx]
        
        if current_sheet_idx != res["sheet_idx"]:
            current_sheet_idx = res["sheet_idx"]
            grid_data = load_data(sheets[current_sheet_idx])
            
        highlight_pos = (res["row"], res["col"])

def mouse_callback(event, x, y, flags, param):
    global highlight_pos
    if event == cv2.EVENT_LBUTTONDOWN:
        # Click vào bảng kết quả bên phải
        if x >= PANEL_RIGHT_X and y >= 120:
            click_idx = (y - 120) // 28
            if click_idx < len(search_results):
                select_result_item(click_idx)
                
        # Click vào sơ đồ Rack bên trái
        elif x < RACK_VIEW_W and y >= MARGIN_Y:
            rows, cols = grid_data.shape
            cell_w = VIEW_W / max(cols, 1)
            cell_h = VIEW_H / max(rows, 1)
            
            real_x = x - MARGIN_X
            real_y = y - MARGIN_Y
            
            if real_x >= 0 and real_y >= 0:
                col = int(real_x // cell_w)
                row = int(real_y // cell_h)
                
                if 0 <= row < rows and 0 <= col < cols:
                    if grid_data[row, col].strip():
                        highlight_pos = (row, col)

cv2.namedWindow("RACK MANAGEMENT - OPENCV", cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback("RACK MANAGEMENT - OPENCV", mouse_callback)

while True:
    rows, cols = grid_data.shape
    canvas = np.ones((WIN_H, WIN_W, 3), dtype=np.uint8) * 255

    flash_on = (int(time.time() * 4) % 2 == 0)

    # TỰ ĐỘNG TÍNH KÍCH THƯỚC Ô ĐỂ HIỂN THỊ TRỌN VẸN (AUTO-FIT)
    cell_w = VIEW_W / max(cols, 1)
    cell_h = VIEW_H / max(rows, 1)
    
    # Tự động tính cỡ chữ và độ dài chuỗi hiển thị theo kích thước ô
    font_scale = max(0.2, min(0.45, cell_h / 60.0))
    max_char_len = max(3, int(cell_w / 7))

    # ==================== BÊN TRÁI: GIAO DIỆN SƠ ĐỒ RACK ====================
    for r in range(rows):
        for c in range(cols):
            x1 = int(MARGIN_X + c * cell_w)
            y1 = int(MARGIN_Y + r * cell_h)
            x2 = int(MARGIN_X + (c + 1) * cell_w)
            y2 = int(MARGIN_Y + (r + 1) * cell_h)

            val = grid_data[r, c].strip()
            
            bg_color = (255, 255, 255)
            text_color = (0, 0, 0)
            border_color = (210, 210, 210)
            border_thick = 1

            if "Tang 3" in val: bg_color = COLOR_TANG3
            elif "Tang 2" in val: bg_color = COLOR_TANG2
            elif "Tang 1" in val: bg_color = COLOR_TANG1
            elif "Khu" in val: bg_color = COLOR_KHU

            if highlight_pos == (r, c):
                bg_color = (0, 0, 255) if flash_on else (0, 255, 255)
                text_color = (255, 255, 255) if flash_on else (0, 0, 0)
                border_color = (0, 0, 0)
                border_thick = 2

            cv2.rectangle(canvas, (x1, y1), (x2, y2), bg_color, -1)
            cv2.rectangle(canvas, (x1, y1), (x2, y2), border_color, border_thick)

            if val:
                disp_val = val[:max_char_len]
                thick = 1 if "Tang" not in val else 2
                
                # Căn chữ vào giữa ô
                text_offset_y = int(y1 + (cell_h + 8) / 2)
                cv2.putText(canvas, disp_val, (x1 + 2, text_offset_y),
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thick, cv2.LINE_AA)

    # Thanh Tiêu Đề Cố Định
    cv2.rectangle(canvas, (0, 0), (RACK_VIEW_W, MARGIN_Y - 5), (245, 250, 245), -1)
    cv2.line(canvas, (0, MARGIN_Y - 5), (RACK_VIEW_W, MARGIN_Y - 5), (180, 200, 180), 2)
    cv2.line(canvas, (RACK_VIEW_W + 5, 0), (RACK_VIEW_W + 5, WIN_H), (200, 200, 200), 2)

    cv2.putText(canvas, f"Sheet: {sheets[current_sheet_idx]} ({rows}x{cols} cells - Auto-Fit Full View)", (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 100, 0), 2)
    cv2.putText(canvas, "[TAB: Doi Sheet | UP/DOWN: Chon ket qua]", (15, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (80, 80, 80), 1)

    # ==================== BÊN PHẢI: BẢNG KẾT QUẢ TÌM KIẾM ====================
    cv2.putText(canvas, "TIM KIEM SAN PHAM / MA RACK", (PANEL_RIGHT_X, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 0, 0), 2)
    cv2.rectangle(canvas, (PANEL_RIGHT_X, 35), (WIN_W - 15, 68), (255, 255, 255), -1)
    cv2.rectangle(canvas, (PANEL_RIGHT_X, 35), (WIN_W - 15, 68), (0, 150, 255), 2)
    cv2.putText(canvas, f"{search_text}_", (PANEL_RIGHT_X + 10, 58),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1)

    tbl_x, tbl_y, row_h = PANEL_RIGHT_X, 90, 28
    col_w = [40, 90, 140, 115]
    headers = ["STT", "Sheet", "Mã Hàng", "Tọa Độ"]

    # Header Bảng
    hx = tbl_x
    for i, h_text in enumerate(headers):
        w = col_w[i]
        cv2.rectangle(canvas, (hx, tbl_y), (hx + w, tbl_y + row_h), EXCEL_HEADER_BG, -1)
        cv2.rectangle(canvas, (hx, tbl_y), (hx + w, tbl_y + row_h), EXCEL_GRID_BORDER, 1)
        cv2.putText(canvas, h_text, (hx + 5, tbl_y + 19),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 1, cv2.LINE_AA)
        hx += w

    # Danh sách Kết quả
    max_visible_rows = (WIN_H - tbl_y - row_h - 10) // row_h
    for i in range(min(len(search_results), max_visible_rows)):
        res = search_results[i]
        ry = tbl_y + row_h + i * row_h
        r_bg = EXCEL_SELECT_ROW if i == selected_result_idx else (255, 255, 255)
        
        row_data = [
            str(i + 1),
            str(res['sheet_name']),
            str(res['val']),
            f"R:{res['row']} C:{res['col']}"
        ]

        rx = tbl_x
        for j, cell_val in enumerate(row_data):
            w = col_w[j]
            cv2.rectangle(canvas, (rx, ry), (rx + w, ry + row_h), r_bg, -1)
            cv2.rectangle(canvas, (rx, ry), (rx + w, ry + row_h), EXCEL_GRID_BORDER, 1)
            cv2.putText(canvas, cell_val[:16], (rx + 5, ry + 19),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
            rx += w

    cv2.imshow("RACK MANAGEMENT - OPENCV", canvas)

    key = cv2.waitKey(20) & 0xFF
    if key == 27: # ESC
        break
    elif key == 9: # TAB
        current_sheet_idx = (current_sheet_idx + 1) % len(sheets)
        grid_data = load_data(sheets[current_sheet_idx])
        highlight_pos = None
    elif key in (8, 127): # Backspace
        search_text = search_text[:-1]
        update_global_search(search_text)
        if search_results: select_result_item(0)
        else: highlight_pos = None
    elif key == 13: # Enter
        if search_results: select_result_item(0)
    elif key == 0: # Mũi tên UP
        if search_results and selected_result_idx > 0:
            select_result_item(selected_result_idx - 1)
    elif key == 1: # Mũi tên DOWN
        if search_results and selected_result_idx < len(search_results) - 1:
            select_result_item(selected_result_idx + 1)
    elif 32 <= key <= 126:
        search_text += chr(key)
        update_global_search(search_text)
        if search_results: select_result_item(0)

cv2.destroyAllWindows()