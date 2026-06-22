import streamlit as st
from .utils import save_db

def show_story_page():
    st.header("📖 הספר שלי - עריכת תוכן")

    if 'db' not in st.session_state or st.session_state.db is None:
        st.warning("נא פתח פרויקט.")
        return

    db = st.session_state.db
    
    # --- תצוגת גודל הפרויקט בעמודים עם אפשרות עריכה ---
    st.write("### 📏 גודל הפרויקט")
    col_proj1, col_proj2, col_proj3 = st.columns([2, 2, 2])
    
    with col_proj1:
        current_target_pages = db.get("target_pages", 300)
        st.metric("יעד עמודים", current_target_pages)
    
    with col_proj2:
        new_target_pages = st.number_input("עדכן יעד עמודים:", 
                                          value=current_target_pages, 
                                          min_value=1, 
                                          step=10,
                                          key="target_pages_edit")
        if new_target_pages != current_target_pages:
            db["target_pages"] = new_target_pages
            # עדכן את target_tokens של כל פרק בהתאם לחלוקה חדשה
            chapters_list = db.get("chapters", [])
            num_chapters = len(chapters_list)
            if num_chapters > 0:
                new_avg_tokens = int((new_target_pages * 250) / num_chapters)
                for chapter in chapters_list:
                    chapter["target_tokens"] = new_avg_tokens
            save_db()
            st.success(f"✅ גודל הפרויקט עודכן ל-{new_target_pages} עמודים! יעד הפרקים עודכן ל-{new_avg_tokens} מילים לפרק.")
            st.rerun()
    
    with col_proj3:
        total_target_words = db.get("target_pages", 300) * 250
        st.metric("יעד מילים (בהערכה)", f"{total_target_words:,}")
    
    st.divider()
    
    # שליפת הפרק שנבחר מהסיידבר
    sel_id = st.session_state.get('sel_c_id')
    chapters_list = db.get("chapters", [])
    chapter = next((c for c in chapters_list if c["id"] == sel_id), None)

    if not chapter:
        st.info("👈 בחר פרק מהתפריט הימני כדי לצפות בתוכן שלו או לערוך אותו.")
        return

    # --- מנגנון וידוא מבנה גרסאות ---
    if "content_data" not in chapter:
        old_text = chapter.get("content", "")
        chapter["content_data"] = {"current": old_text, "versions": []}

    st.subheader(f"עורך: {chapter['name']}")
    
    # תזכורת תכנון
    with st.expander("📌 תזכורת תכנון (Beats ותקציר)", expanded=False):
        st.write(f"**מיקום:** {chapter.get('location', 'לא הוגדר')}")
        st.write(f"**Beats:** {chapter.get('beats', 'אין ביטים')}")

    # תיבת העריכה המרכזית
    content = st.text_area("תוכן הפרק:", 
                           value=chapter["content_data"]["current"], 
                           height=500,
                           key=f"edit_{chapter['id']}")

    # כפתור שמירה
    if st.button("💾 שמור שינויים בפרק", use_container_width=True):
        chapter["content_data"]["current"] = content
        chapter["content"] = content 
        save_db()
        st.success(f"התוכן של '{chapter['name']}' נשמר בהצלחה!")
        st.rerun()

    # --- חישובי מילים ויעדים ---
    # 1. מילים בפרק נוכחי
    word_count = len(content.split())
    
    # 2. חישוב יעד ממוצע
    # ננסה לשלוף את יעד העמודים מהפרויקט. אם מוגדר ב-300 עמודים, נניח 250 מילים לעמוד.
    target_pages = db.get("target_pages", 300)
    total_word_target = target_pages * 250 # הערכה סטנדרטית
    num_chapters = len(chapters_list)
    
    avg_target_per_chapter = int(total_word_target / num_chapters) if num_chapters > 0 else 0

    # תצוגת המדדים
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("מילים בפרק", word_count)
    col_m2.metric("יעד ממוצע לפרק", avg_target_per_chapter)
    
    # חישוב אחוז ביצוע לפרק הזה
    progress = min(word_count / avg_target_per_chapter, 1.0) if avg_target_per_chapter > 0 else 0
    col_m3.write(f"**התקדמות לפרק:** {int(progress*100)}%")
    st.progress(progress)

    st.divider()

    # --- הצגת היסטוריית גרסאות ---
    st.subheader("📜 גרסאות קודמות מהרנדר")
    versions = chapter["content_data"].get("versions", [])

    if not versions:
        st.info("עדיין אין גרסאות קודמות לפרק זה.")
    else:
        for i, version_data in enumerate(versions):
            version_num = len(versions) - i
            # הסקת הטקסט מהגרסה (יכול להיות string או dict)
            version_text = version_data.get("text") if isinstance(version_data, dict) else version_data
            timestamp = version_data.get("timestamp", "") if isinstance(version_data, dict) else ""
            
            with st.expander(f"🕰️ גרסה {version_num} {f'({timestamp})' if timestamp else ''}"):
                st.text_area(f"טקסט גרסה {version_num}:", 
                             value=version_text, 
                             height=250, 
                             key=f"ver_view_{chapter['id']}_{i}",
                             disabled=True)
                
                if st.button(f"⏪ שחזר גרסה {version_num}", key=f"restore_{chapter['id']}_{i}"):
                    # שמירה של ה-current כגרסה חדשה
                    current_before_restore = chapter["content_data"]["current"]
                    chapter["content_data"]["versions"].insert(0, {
                        "text": current_before_restore,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    # החזרת הגרסה
                    chapter["content_data"]["current"] = version_text
                    chapter["content"] = version_text
                    save_db()
                    st.success("הגרסה שוחזרה!")
                    st.rerun()