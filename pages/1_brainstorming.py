import streamlit as st
from components.utils import save_db, apply_rtl

st.set_page_config(page_title="סיעור מוחות", layout="wide")
apply_rtl()

st.title("🧠 סיעור מוחות ליצירת הסיפור")
st.info("מרחב זה ישמש בעתיד ליצירת רעיונות, עלילות ודמויות בעזרת AI.")

if st.button("חזרה לדף הניהול"):
    st.switch_page("app.py")