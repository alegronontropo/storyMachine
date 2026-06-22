import streamlit as st
from .utils import save_db

def show_world():
    st.subheader("🌍 הגדרות עולם ואווירה")

    # 1. וידוא קיום מפתח world בבסיס הנתונים
    if "world" not in st.session_state.db:
        st.session_state.db["world"] = {}
    
    world_data = st.session_state.db["world"]

    # --- חלונית תצוגה לקריאה בלבד ---
    with st.expander("👁️ תצוגה מהירה של הגדרות העולם", expanded=False):
        st.markdown(f"### {world_data.get('world_name', 'טרם הוגדר שם')}")
        st.write(f"**תקופה:** {world_data.get('year', 'לא הוגדרה')}")
        
        st.markdown("---")
        col_view1, col_view2 = st.columns(2)
        with col_view1:
            st.markdown("**הבורא/כוח עליון:**")
            st.info(world_data.get('creator', 'אין מידע'))
            
            st.markdown("**מבנה חברתי ופוליטי:**")
            st.info(world_data.get('social_structure', 'אין מידע'))
            
        with col_view2:
            st.markdown("**טכנולוגיה וקסם:**")
            st.info(world_data.get('tech_magic', 'אין מידע'))
            
        st.markdown("**📜 נספחים ותרבות:**")
        st.caption(world_data.get('notes', 'אין נספחים רשומים'))

    st.divider()

    # --- טופס עריכת העולם ---
    with st.form("world_design_form"):
        st.write("### 🖋️ עריכת הגדרות העולם")
        
        col1, col2 = st.columns(2)
        with col1:
            w_name = st.text_input("שם עולם / האזור המרכזי:", value=world_data.get("world_name", "סהר הפורה"))
        with col2:
            w_year = st.text_input("השנה בסיפור:", value=world_data.get("year", "2000-1600 לפנה״ס"))

        st.write("---")
        st.write("### 🏛️ חוקי העולם ואווירה")
        
        w_creator = st.text_area("הבורא / כוח עליון (תפיסה פילוסופית):", 
                                 value=world_data.get("creator", ""), height=100)
        
        w_social = st.text_area("מבנה חברתי ופוליטי:", 
                                value=world_data.get("social_structure", ""), height=100)
        
        w_tech = st.text_area("טכנולוגיה / קסם / ידע:", 
                              value=world_data.get("tech_magic", ""), height=100)

        st.write("---")
        w_notes = st.text_area("📚 נספחים ותרבות (מידע להזרקה לסצנות - ברונזה, רפואה, חיות, זכוכית):", 
                               value=world_data.get("notes", ""), height=400)

        if st.form_submit_button("💾 שמור הגדרות עולם"):
            st.session_state.db["world"].update({
                "world_name": w_name,
                "year": w_year,
                "creator": w_creator,
                "social_structure": w_social,
                "tech_magic": w_tech,
                "notes": w_notes
            })
            save_db()
            st.success("הגדרות העולם נשמרו בהצלחה!")
            st.rerun()