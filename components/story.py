import streamlit as st
from .utils import save_db
import uuid

def show_story_page():
    st.subheader("📖 ניהול מבנה הסיפור")
    db = st.session_state.db

    # וודוא מבנה בסיסי
    for key in ["parts", "sequences", "chapters"]:
        if key not in db: db[key] = []

    # --- א. הוספה מהירה ---
    with st.expander("➕ הוספת איבר חדש לעץ"):
        col1, col2, col3 = st.columns(3)
        with col1:
            item_type = st.selectbox("סוג:", ["חלק", "סיקוונס", "פרק"])
            new_title = st.text_input("כותרת פריט:")
        with col2:
            parent_id = None
            if item_type == "סיקוונס":
                p_options = {p['id']: p['name'] for p in db["parts"]}
                parent_id = st.selectbox("שייך לחלק:", options=list(p_options.keys()), format_func=lambda x: p_options[x])
            elif item_type == "פרק":
                s_options = {s['id']: s['name'] for s in db["sequences"]}
                parent_id = st.selectbox("שייך לסיקוונס:", options=list(s_options.keys()), format_func=lambda x: s_options[x])
        with col3:
            st.write(" ")
            if st.button("הוסף למפה", use_container_width=True):
                if new_title:
                    add_item_to_tree(item_type, new_title, parent_id)
                    st.rerun()

    st.divider()

    # --- ב. תצוגת ניהול עץ ---
    if not db["parts"]:
        st.info("הסיפור ריק. התחל בהוספת 'חלק' חדש.")
        return

    # מעבר על חלקים
    for p in sorted(db["parts"], key=lambda x: x.get('order', 0)):
        col_p1, col_p2 = st.columns([0.8, 0.2])
        new_p_name = col_p1.text_input(f"חלק {p.get('order', 0)}:", value=p['name'], key=f"edit_p_{p['id']}")
        if new_p_name != p['name']:
            p['name'] = new_p_name
            save_db()
        
        render_item_controls(p, "parts") 

        # סיקוונסים
        p_seqs = [s for s in db["sequences"] if s.get('part_id') == p['id']]
        for s in sorted(p_seqs, key=lambda x: x.get('order', 0)):
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;🔹 **סיקוונס: {s['name']}**")
            col_s1, col_s2 = st.columns([0.1, 0.9])
            with col_s2:
                col_sn1, col_sn2 = st.columns([0.7, 0.3])
                new_s_name = col_sn1.text_input(f"ערוך שם סיקוונס:", value=s['name'], key=f"edit_s_{s['id']}", label_visibility="collapsed")
                if new_s_name != s['name']:
                    s['name'] = new_s_name
                    save_db()
                render_item_controls(s, "sequences", indent=True)

                # פרקים
                s_chaps = [c for c in db["chapters"] if c.get('seq_id') == s['id']]
                for c in sorted(s_chaps, key=lambda x: x.get('order', 0)):
                    col_c1, col_c2 = st.columns([0.1, 0.9])
                    with col_c2:
                        col_cn1, col_cn2 = st.columns([0.6, 0.4])
                        new_c_name = col_cn1.text_input(f"📄 פרק:", value=c['name'], key=f"edit_c_{c['id']}", label_visibility="collapsed")
                        if new_c_name != c['name']:
                            c['name'] = new_c_name
                            save_db()
                        render_item_controls(c, "chapters", indent=True)
            st.markdown("---")

def render_item_controls(item, table_key, indent=False):
    col_spacer, col_up, col_down, col_del = st.columns([0.7, 0.1, 0.1, 0.1])
    
    if col_up.button("↑", key=f"up_{item['id']}"):
        move_item(item['id'], table_key, -1.5)
    if col_down.button("↓", key=f"down_{item['id']}"):
        move_item(item['id'], table_key, 1.5)
    if col_del.button("🗑️", key=f"del_{item['id']}"):
        delete_item(item['id'], table_key)
        st.rerun()

def move_item(item_id, table_key, direction):
    db = st.session_state.db
    items = db[table_key]
    
    # 1. מצא את האובייקט שזז
    target_item = next((i for i in items if i['id'] == item_id), None)
    if not target_item: return

    # 2. עדכן לו את ה-order זמנית
    target_item['order'] += direction
    
    # 3. זהה את הקבוצה שצריכה סידור מחדש (לפי הורה)
    if table_key == "parts":
        siblings = items
    elif table_key == "sequences":
        siblings = [i for i in items if i.get('part_id') == target_item.get('part_id')]
    else: # chapters
        siblings = [i for i in items if i.get('seq_id') == target_item.get('seq_id')]
    
    # 4. מיין את הקבוצה לפי ה-order החדש ועדכן למספרים שלמים 1, 2, 3...
    sorted_siblings = sorted(siblings, key=lambda x: x.get('order', 0))
    for idx, obj in enumerate(sorted_siblings):
        obj['order'] = idx + 1
        
    save_db()
    st.rerun()

def add_item_to_tree(item_type, name, parent_id):
    db = st.session_state.db
    new_id = str(uuid.uuid4())[:8]
    type_map = {"חלק": "parts", "סיקוונס": "sequences", "פרק": "chapters"}
    key = type_map[item_type]
    
    siblings = []
    if item_type == "חלק":
        siblings = db["parts"]
    elif item_type == "סיקוונס":
        siblings = [i for i in db["sequences"] if i.get('part_id') == parent_id]
    elif item_type == "פרק":
        siblings = [i for i in db["chapters"] if i.get('seq_id') == parent_id]
        
    order = len(siblings) + 1
    
    new_item = {"id": new_id, "name": name, "order": order}
    if item_type == "סיקוונס": new_item["part_id"] = parent_id
    if item_type == "פרק": 
        new_item["seq_id"] = parent_id
        # חישוב target_tokens על בסיס target_pages של הפרויקט
        target_pages = db.get("target_pages", 300)
        num_chapters = len(db.get("chapters", [])) + 1  # כולל הפרק החדש
        target_tokens = int((target_pages * 250) / num_chapters) if num_chapters > 0 else 250
        new_item.update({"beats": "", "summary": "", "location": "כללי", "characters": [], "chapter_goal": "", "start_point": "", "end_point": "", "target_tokens": target_tokens})
    
    db[key].append(new_item)
    save_db()

def delete_item(item_id, table_key):
    db = st.session_state.db
    if table_key == "parts":
        seq_ids = [s['id'] for s in db["sequences"] if s.get('part_id') == item_id]
        db["chapters"] = [c for c in db["chapters"] if c.get('seq_id') not in seq_ids]
        db["sequences"] = [s for s in db["sequences"] if s.get('part_id') != item_id]
        db["parts"] = [p for p in db["parts"] if p['id'] != item_id]
    elif table_key == "sequences":
        db["chapters"] = [c for c in db["chapters"] if c.get('seq_id') != item_id]
        db["sequences"] = [s for s in db["sequences"] if s['id'] != item_id]
    elif table_key == "chapters":
        db["chapters"] = [c for c in db["chapters"] if c['id'] != item_id]
    save_db()