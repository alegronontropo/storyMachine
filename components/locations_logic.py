import streamlit as st

from .utils import save_db



def show_locations_page():

    st.subheader("📍 ניהול מקומות ותתי-מקומות")



    # וידוא קיום מילון המקומות בבסיס הנתונים

    if "locations" not in st.session_state.db:

        st.session_state.db["locations"] = {}



    locs_dict = st.session_state.db["locations"]

    loc_names = list(locs_dict.keys())



    # --- א. בחירת מקום ראשי לעריכה/יצירה ---

    options = ["➕ הוסף מקום ראשי חדש"] + loc_names

    selected_main = st.selectbox("בחר מקום ראשי לניהול:", options)



    is_edit = selected_main != "➕ הוסף מקום ראשי חדש"

    current_data = locs_dict.get(selected_main, {"sub_locations": {}}) if is_edit else {"sub_locations": {}}



    # --- ב. הצגת מפת האתר (תצוגה מהירה) ---

    if is_edit:

        st.info(f"עורך כעת את: **{selected_main}**")

        sub_locs = current_data.get("sub_locations", {})

        if sub_locs:

            st.caption(f"תתי-מקומות קיימים: {', '.join(sub_locs.keys())}")



    # --- ג. טופס מקום ראשי ---

    with st.form("main_loc_form"):

        st.write(f"### {'עריכת מקום: ' + selected_main if is_edit else 'מקום ראשי חדש'}")

       

        m_name = st.text_input("שם המקום הראשי:", value=selected_main if is_edit else "")

        col1, col2 = st.columns(2)

        with col1:

            m_world_pos = st.text_area("מיקום בעולם (גאוגרפיה/מרחק):", value=current_data.get("world_pos", ""))

            m_climate = st.text_area("אקלים ותאורה כללית:", value=current_data.get("climate", ""))

        with col2:

            m_acoustics = st.text_area("אקוסטיקה ותנועה:", value=current_data.get("acoustics", ""))

            m_general_desc = st.text_area("תיאור 'גג' כללי:", value=current_data.get("general_desc", ""))



        if st.form_submit_button("💾 שמור מקום ראשי"):

            if m_name:

                # יצירת המבנה במידה וחדש

                if m_name not in st.session_state.db["locations"]:

                    st.session_state.db["locations"][m_name] = {"sub_locations": {}}

               

                # עדכון הנתונים (שמירה על תתי-מקומות קיימים)

                st.session_state.db["locations"][m_name].update({

                    "world_pos": m_world_pos,

                    "climate": m_climate,

                    "acoustics": m_acoustics,

                    "general_desc": m_general_desc

                })

                save_db()

                st.success(f"המקום {m_name} נשמר!")

                st.rerun()

            else:

                st.error("חובה להזין שם למקום.")



    st.divider()



    # --- ד. ניהול תתי-מקומות (יופיע רק עבור מקום קיים) ---

    if is_edit:

        st.subheader(f"🏠 חללים פנימיים בתוך: {selected_main}")

       

        sub_locs = current_data.get("sub_locations", {})

        sub_options = ["➕ הוסף תת-מקום חדש"] + list(sub_locs.keys())

        selected_sub = st.selectbox("בחר תת-מקום לעריכה:", sub_options)

       

        is_sub_edit = selected_sub != "➕ הוסף תת-מקום חדש"

        current_sub_data = sub_locs.get(selected_sub, {}) if is_sub_edit else {}



        with st.form("sub_loc_form"):

            s_name = st.text_input("שם תת-המקום:", value=selected_sub if is_sub_edit else "")

           

            col3, col4 = st.columns(2)

            with col3:

                s_structure = st.text_area("מבנה וארכיטקטורה:", value=current_sub_data.get("structure", ""))

                s_activity = st.text_area("מוקד פעילות:", value=current_sub_data.get("activity", ""))

            with col4:

                s_senses = st.text_area("חושים (ריח, צליל, מגע):", value=current_sub_data.get("senses", ""))

                s_props = st.text_area("חפצים ופרטים (Props):", value=current_sub_data.get("props", ""))



            submit_label = "עדכן תת-מקום" if is_sub_edit else "הוסף תת-מקום"

            if st.form_submit_button(submit_label):

                if s_name:

                    st.session_state.db["locations"][selected_main]["sub_locations"][s_name] = {

                        "structure": s_structure,

                        "activity": s_activity,

                        "senses": s_senses,

                        "props": s_props

                    }

                    save_db()

                    st.success(f"תת-המקום {s_name} נשמר!")

                    st.rerun()



        # מחיקת תת-מקום

        if is_sub_edit:

            if st.button(f"🗑️ מחק את {selected_sub}"):

                del st.session_state.db["locations"][selected_main]["sub_locations"][selected_sub]

                save_db()

                st.rerun()



    # --- ה. אזור מחיקה למקום ראשי ---

    if is_edit:

        st.write("---")

        with st.expander("⚠️ אזור מסוכן"):

            if st.button(f"🗑️ מחק את כל פרויקט המיקום: {selected_main}", type="primary"):

                del st.session_state.db["locations"][selected_main]

                save_db()

                st.rerun()