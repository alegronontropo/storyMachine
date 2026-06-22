import streamlit as st
import json
import os

def save_db():
    """שומר את מסד הנתונים לקובץ בתוך תיקיית הפרויקט"""
    if st.session_state.db:
        p_name = st.session_state.db.get("project_name", "Unknown_Project")
        if not os.path.exists(p_name):
            os.makedirs(p_name)
        json_path = os.path.join(p_name, "story_factory_data.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.db, f, ensure_ascii=False, indent=4)

def apply_rtl():
    """מחיל עיצוב RTL על האפליקציה"""
    st.markdown("""
        <style>
        div, p, label, input, button, select, [data-baseweb="tab-list"], .stTextArea textarea { 
            direction: rtl !important; 
            text-align: right !important; 
        }
        section[data-testid="stSidebar"] { 
            direction: rtl !important; 
        }
        .stButton button { width: 100%; }
        </style>
    """, unsafe_allow_html=True)


def summarize_characters(chars_data, selected_list, max_chars=300):
    """Return a compact one-line per character summary for prompt injection.

    chars_data: dict of all characters keyed by name
    selected_list: list of character names to summarize
    """
    summaries = []
    for name in selected_list or []:
        c = chars_data.get(name, {})
        role = c.get('role', '')
        traits = c.get('traits', '')
        # pick two salient traits (comma separated) up to short length
        trait_snip = ", ".join([t.strip() for t in (traits.split(',')[:2])]) if traits else ''
        summary = f"{name}: {role.split('.')[0][:80]} {('- ' + trait_snip) if trait_snip else ''}".strip()
        summaries.append(summary)
        # stop early if too long
        if sum(len(s) for s in summaries) > max_chars:
            break

    return "; ".join(summaries)