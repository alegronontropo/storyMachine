import streamlit as st

def show_sidebar_navigation():
    """מציג עץ ניווט נקי ללא רשימות נפתחות - לבחירת פרק בלבד [cite: 7, 10]"""
    st.sidebar.title("🚀 ניווט מהיר")
    
    if 'db' not in st.session_state or st.session_state.db is None:
        st.sidebar.info("פתח פרויקט כדי להתחיל")
        return

    db = st.session_state.db
    sel_id = st.session_state.get('sel_c_id')

    # מעבר היררכי על החלקים
    for p in sorted(db.get("parts", []), key=lambda x: x.get("order", 0)):
        st.sidebar.markdown(f"### 📁 {p['name']}")
        
        # סיקוונסים בתוך חלק
        p_seqs = [s for s in db.get("sequences", []) if s.get("part_id") == p["id"]]
        for s in sorted(p_seqs, key=lambda x: x.get("order", 0)):
            st.sidebar.markdown(f"&nbsp;&nbsp;&nbsp;**🔹 {s['name']}**")
            
            # פרקים בתוך סיקוונס
            s_chaps = [c for c in db.get("chapters", []) if c.get("seq_id") == s["id"]]
            for c in sorted(s_chaps, key=lambda x: x.get("order", 0)):
                # הדגשת הפרק הנבחר
                label = f"📖 {c['name']}"
                if c['id'] == sel_id:
                    label = f"🎯 {c['name']} (פעיל)"
                
                if st.sidebar.button(label, key=f"side_{c['id']}", use_container_width=True):
                    st.session_state.sel_c_id = c["id"]
                    st.rerun()
        
        st.sidebar.divider()
    
    st.sidebar.caption("טיפ: בחירת פרק תטען אותו לטאב רנדר [cite: 15]")