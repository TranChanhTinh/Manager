else:
            st.warning("Hãy bấm chọn ô đang có thùng hàng trước.")
    else:
        src_sheet, src_r, src_c = st.session_state.move_source
        src_df = cached_sheet(src_sheet)
        src_val = str(src_df.iat[src_r, src_c]).strip()
        st.info(f"Đang di chuyển **{src_val}** từ {src_sheet} — {position_text(src_r, src_c)}. Bấm một ô đích trên sơ đồ.")
        target_is_valid = selected is not None and (st.session_state.current_sheet, selected[0], selected[1]) != (src_sheet, src_r, src_c)
        if target_is_valid:
            target_val = str(df.iat[selected[0], selected[1]]).strip()
            a, b = st.columns([1, 1])
            with a:
                if st.button(f"✅ Chuyển đến ô này ({target_val or 'trống'})", use_container_width=True):
                    if is_label(target_val):
                        write_cell(src_sheet, src_r, src_c, "")
                        write_cell(st.session_state.current_sheet, selected[0], selected[1], src_val)
                        st.session_state.move_mode = False
                        st.session_state.move_source = None
                        st.session_state.notice = f"Đã chuyển {src_val} đến {st.session_state.current_sheet}, {position_text(*selected)}."
                        st.rerun()
                    else:
                        st.error("Ô đích đã có hàng. Hãy chọn ô trống để tránh ghi đè.")
            with b:
                if st.button("Hủy di chuyển", use_container_width=True):
                    st.session_state.move_mode = False
                    st.session_state.move_source = None
                    st.rerun()
        elif st.button("Hủy di chuyển"):
            st.session_state.move_mode = False
            st.session_state.move_source = None
            st.rerun()

elif action == "Thêm / sửa thùng":
    if selected:
        new_value = st.text_input("Mã thùng / nội dung", value=selected_value, key=f"edit_{st.session_state.current_sheet}_{selected[0]}_{selected[1]}")
        if st.button("💾 Lưu vào ô đang chọn", type="primary"):
            if not is_label(selected_value) or not is_label(new_value):
                write_cell(st.session_state.current_sheet, selected[0], selected[1], new_value.strip())
                st.session_state.notice = f"Đã cập nhật {position_text(*selected)}."
                st.rerun()
            else:
                st.warning("Không thể ghi đè ô nhãn tầng/khu hoặc ô trống bằng nội dung rỗng.")
    else:
        st.info("Bấm một ô trên sơ đồ trước, sau đó nhập mã thùng để thêm hoặc sửa.")

elif action == "Xóa / xuất hàng":
    if selected and not is_label(selected_value):
        st.warning(f"Sẽ xóa mã **{selected_value}** tại {position_text(*selected)}.")
        confirm = st.checkbox("Tôi xác nhận muốn xóa / xuất thùng này", key="confirm_delete")
        if st.button("🗑️ Xóa thùng khỏi vị trí", type="primary", disabled=not confirm):
            write_cell(st.session_state.current_sheet, selected[0], selected[1], "")
            st.session_state.selected_pos = None
            st.session_state.notice = "Đã xóa thùng khỏi vị trí."
            st.rerun()
    else:
        st.info("Bấm vào ô đang chứa thùng cần xóa.")

st.divider()
st.subheader("🗺️ Sơ đồ vị trí — bấm trực tiếp vào ô")
if action == "Di chuyển thùng" and st.session_state.move_mode:
    st.caption("Chế độ chọn đích: hãy chọn sheet đích ở Sidebar nếu cần, rồi bấm ô đích bên dưới.")

# Render every cell as a real Streamlit button. Clicking a cell selects it.
# Color is communicated with prefixes to work consistently across Streamlit versions.
current_tier = ""
for r in range(df.shape[0]):
    row_vals = [str(df.iat[r, c]).strip() for c in range(df.shape[1])]
    for val in row_vals:
        low = val.lower()
        if "tang 3" in low:
            current_tier = "Tang 3"
        elif "tang 2" in low:
            current_tier = "Tang 2"
        elif "tang 1" in low:
            current_tier = "Tang 1"

    cols = st.columns(df.shape[1], gap="small")
    for c in range(df.shape[1]):
        val = str(df.iat[r, c]).strip()
        low = val.lower()
        if "tang 3" in low:
            label = f"🟣 {val}"
        elif "tang 2" in low:
            label = f"🔵 {val}"
        elif "tang 1" in low:
            label = f"🟢 {val}"
        elif "khu" in low:
            label = f"🟠 {val}"
        elif not val:
            label = "＋ Trống"
        else:
            prefix = "🟣" if current_tier == "Tang 3" else "🔵" if current_tier == "Tang 2" else "🟢" if current_tier == "Tang 1" else "📦"
            label = f"{prefix} {val}"

        is_selected = selected == (r, c)
        if is_selected:
            label = f"👉 {val or 'Ô trống'}"
        key = f"cell_{st.session_state.current_sheet}_{r}_{c}"
        with cols[c]:
            if st.button(label, key=key, help=f"{position_text(r, c)}" + (f" · {val}" if val else "")):
                st.session_state.selected_pos = (r, c)
                st.rerun()

st.divider()
with open(EXCEL_PATH, "rb") as f:
    st.download_button(
        "📥 Tải báo cáo Excel",
        data=f.read(),
        file_name="RACK_WMS_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
st.caption("Lưu ý: đóng file RACK.xlsx trong Excel trước khi thao tác để tránh xung đột khi lưu.")
