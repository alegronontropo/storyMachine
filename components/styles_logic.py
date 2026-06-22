import streamlit as st
import os

STYLES_DIR = 'styles'

def ensure_styles_dir():
    if not os.path.exists(STYLES_DIR):
        os.makedirs(STYLES_DIR)

def get_style_metadata(filename):
    file_path = os.path.join(STYLES_DIR, filename)
    display_name = filename.replace('.txt', '')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith("# Name:"):
                display_name = first_line.replace("# Name:", "").strip()
    except:
        pass
    return display_name

def get_all_styles_map():
    ensure_styles_dir()
    styles_map = {}
    files = [f for f in os.listdir(STYLES_DIR) if f.endswith('.txt')]
    for f in files:
        display_name = get_style_metadata(f)
        styles_map[display_name] = f
    return styles_map

def load_style_content(filename):
    file_path = os.path.join(STYLES_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # מחזיר את כל הטקסט חוץ משורת השם הראשונה
            if lines and lines[0].startswith("# Name:"):
                return "".join(lines[1:]).strip()
            return "".join(lines).strip()
    return ""

def save_style(display_name, content, original_filename=None):
    ensure_styles_dir()
    if original_filename:
        filename = original_filename
    else:
        # יצירת שם קובץ תקני משם הסגנון
        safe_name = "".join([c for c in display_name if c.isalnum() or c == '_']).lower()
        filename = f"style_{safe_name}.txt"
    
    file_path = os.path.join(STYLES_DIR, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# Name: {display_name}\n")
        f.write(content)
    return filename

def show_styles_page():
    st.subheader("🖋️ ספריית סגנונות מרכזית")
    
    styles_map = get_all_styles_map()
    display_names = list(styles_map.keys())

    options = ["➕ הוסף סגנון חדש"] + display_names
    selected_display = st.selectbox("בחר סגנון לניהול:", options)

    is_edit = selected_display != "➕ הוסף סגנון חדש"
    
    if is_edit:
        target_file = styles_map[selected_display]
        current_content = load_style_content(target_file)
    else:
        target_file = None
        current_content = ""

    with st.form("style_form_v3"):
        new_display_name = st.text_input("שם הסגנון (למשל: דאגלאס אדאמס, מתח קצבי):", 
                                        value=selected_display if is_edit else "")
        
        st.caption("הנחיות ל-AI: תאר כאן את אוצר המילים, אורך המשפטים והטון המבוקש.")
        s_content = st.text_area("הוראות סגנון:", value=current_content, height=350)

        if st.form_submit_button("💾 שמור סגנון"):
            if new_display_name:
                save_style(new_display_name, s_content, original_filename=target_file)
                st.success(f"הסגנון '{new_display_name}' נשמר בהצלחה!")
                st.rerun()
            else:
                st.error("חובה להזין שם לסגנון.")

    if is_edit:
        st.write("---")
        if st.button(f"🗑️ מחק סגנון: {selected_display}"):
            file_to_del = os.path.join(STYLES_DIR, target_file)
            if os.path.exists(file_to_del):
                os.remove(file_to_del)
                st.warning(f"הסגנון {selected_display} נמחק.")
                st.rerun()