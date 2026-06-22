import streamlit as st
from sidebar import show_sidebar_navigation

st.set_page_config(page_title="Story Machine", layout="wide")

st.title("Story Machine")

show_sidebar_navigation()

st.markdown("---")
st.write("בחר פרק מהסרגל הניווט בצד והמשך ליצירת הסיפור.")
