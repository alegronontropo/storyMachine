import streamlit as st
from datetime import datetime
from .utils import save_db

def add_log_entry(message):
    """מוסיף שורה ללוג בתוך ה-DB ושומר"""
    if 'db' in st.session_state and st.session_state.db is not None:
        if "logs" not in st.session_state.db:
            st.session_state.db["logs"] = []
        
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        log_text = f"[{timestamp}] {message}"
        
        st.session_state.db["logs"].append(log_text)
        save_db()

def show_log_page():
    st.subheader("📜 יומן פעילות הפרויקט")
    
    if "logs" not in st.session_state.db or not st.session_state.db["logs"]:
        st.info("אין עדיין רישומים ביומן.")
        return

    # הצגת הלוגים מהחדש לישן בתוך קופסה מעוצבת
    all_logs = "\n".join(reversed(st.session_state.db["logs"]))
    st.text_area("היסטוריית פעולות:", value=all_logs, height=400, disabled=True)
    
    if st.button("🗑️ נקה יומן"):
        st.session_state.db["logs"] = []
        save_db()
        st.rerun()