import streamlit as st
from sidebar import show_sidebar_navigation
from components.utils import save_db, apply_rtl
from components.supabase_client import (
    get_current_user,
    login_user,
    sign_up_user,
    logout_user,
    load_project_data,
)
import uuid
import json
import os

st.set_page_config(page_title="Story Machine", layout="wide")
apply_rtl()

st.title("Story Machine")

if "project_name" not in st.session_state:
    st.session_state.project_name = ""

with st.sidebar.expander("🔐 התחברות וסנכרון Supabase", expanded=True):
    user = get_current_user()
    if user:
        st.success(f"מחובר כ־{user.get('email', user.get('id', 'משתמש'))}")
        if st.button("התנתק"):
            logout_user()
            st.experimental_rerun()

        st.text_input("שם פרויקט לטעינה/שמירה", key="project_name")
        if st.button("טען פרויקט מ־Supabase"):
            project_name = st.session_state.project_name.strip()
            if not project_name:
                st.warning("יש להזין שם פרויקט.")
            else:
                try:
                    data = load_project_data(project_name)
                    if data:
                        st.session_state.db = data
                        st.success("הפרויקט נטען בהצלחה.")
                    else:
                        st.warning("לא נמצא פרויקט עם השם הזה.")
                except Exception as e:
                    st.error(f"שגיאה בטעינה מ‑Supabase: {e}")

        if st.button("שמור ל‑Supabase"):
            if "db" in st.session_state and st.session_state.db:
                st.session_state.db["project_name"] = st.session_state.project_name or st.session_state.db.get("project_name", "Unknown_Project")
                save_db()
            else:
                st.warning("אין פרויקט לנהל או לשמור.")
    else:
        email = st.text_input("אימייל")
        password = st.text_input("סיסמה", type="password")
        col1, col2 = st.columns(2)
        if col1.button("התחבר"):
            user, error = login_user(email, password)
            if error:
                st.error(error)
            else:
                st.success("התחברת בהצלחה.")
                st.experimental_rerun()
        if col2.button("הרשם"):
            user, error = sign_up_user(email, password)
            if error:
                st.error(error)
            else:
                st.success("נרשמת בהצלחה.")
                st.experimental_rerun()

st.markdown("---")
st.subheader("📚 ניהול פרויקטים")

if "create_mode" not in st.session_state:
    st.session_state.create_mode = False
if "open_mode" not in st.session_state:
    st.session_state.open_mode = False

col_new, col_open = st.columns(2)

with col_new:
    if st.button("➕ צור פרויקט חדש", use_container_width=True, key="btn_create"):
        st.session_state.create_mode = True

with col_open:
    if st.button("📂 פתח פרויקט קיים", use_container_width=True, key="btn_open"):
        st.session_state.open_mode = True

if st.session_state.create_mode:
    new_project_name = st.text_input("שם הפרויקט החדש:", key="create_input")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✅ אישור יצירה", key="confirm_create"):
            if new_project_name.strip():
                st.session_state.db = {
                    "project_name": new_project_name.strip(),
                    "parts": [],
                    "sequences": [],
                    "chapters": [],
                    "characters": {},
                    "locations": {},
                    "world": {},
                    "styles": [],
                    "target_pages": 300,
                    "logs": [],
                }
                save_db()
                st.session_state.create_mode = False
                st.success(f"✅ פרויקט '{new_project_name}' נוצר בהצלחה!")
                st.rerun()
            else:
                st.warning("יש להזין שם לפרויקט.")
    with col_b:
        if st.button("❌ ביטול", key="cancel_create"):
            st.session_state.create_mode = False
            st.rerun()

if st.session_state.open_mode:
    projects_dir = "."
    try:
        projects = [d for d in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, d)) and os.path.exists(os.path.join(projects_dir, d, "story_factory_data.json"))]
        if projects:
            selected_project = st.selectbox("בחר פרויקט:", projects, key="project_select")
            col_c, col_d = st.columns(2)
            with col_c:
                if st.button("✅ טען", key="confirm_open"):
                    project_path = os.path.join(projects_dir, selected_project, "story_factory_data.json")
                    with open(project_path, 'r', encoding='utf-8') as f:
                        st.session_state.db = json.load(f)
                    st.session_state.open_mode = False
                    st.success(f"✅ פרויקט '{selected_project}' נטען בהצלחה!")
                    st.rerun()
            with col_d:
                if st.button("❌ ביטול", key="cancel_open"):
                    st.session_state.open_mode = False
                    st.rerun()
        else:
            st.info("אין פרויקטים קיימים. צור פרויקט חדש כדי להתחיל.")
            if st.button("🔙 חזור", key="back_no_projects"):
                st.session_state.open_mode = False
                st.rerun()
    except Exception as e:
        st.error(f"שגיאה בטעינת פרויקטים: {e}")

st.markdown("---")

if "db" in st.session_state and st.session_state.db:
    show_sidebar_navigation()
    st.subheader(f"📖 {st.session_state.db.get('project_name', 'פרויקט')}")
    st.write("בחר פרק מהסרגל הניווט בצד והמשך ליצירת הסיפור.")
else:
    st.info("👈 בחר 'צור פרויקט חדש' או 'פתח פרויקט קיים' כדי להתחיל.")
